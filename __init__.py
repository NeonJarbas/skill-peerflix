import signal
from os.path import join

import pexpect
from ovos_plugin_common_play.ocp import MediaType, PlaybackType
from ovos_utils.log import LOG
from ovos_workshop.skills.ovos import OVOSSkill


class PeerflixSkill(OVOSSkill):
    def __init__(self):
        super(PeerflixSkill, self).__init__("Peerflix")
        self.supported_media = [MediaType.GENERIC, MediaType.MOVIE]
        self.peerflix = None
        self.running = False
        if "min_buffer_percent" not in self.settings:
            self.settings["min_buffer_percent"] = 2

    def initialize(self):
        self.add_event("skill.peerflix.play", self.stream_torrent)

    def shutdown(self):
        self.stop_peerflix()

    def stop_peerflix(self):
        if self.peerflix:
            self.peerflix.close(force=True)
        if self.peerflix:
            self.peerflix.kill(signal.SIGKILL)
        self.peerflix = None
        self.running = False

    def ocp_play(self, message):
        self.gui.release()
        self.bus.emit(message.reply("ovos.common_play.play",
                                    {"media": message.data}))

    def show_gui(self, footer_text="Launching peerflix"):
        self.gui["footer_text"] = footer_text
        self.gui.show_page(join(self.root_dir, "ui", "BusyPage.qml"))

    def stream_torrent(self, message):
        LOG.debug(f"Streaming torrent: {message.data}")
        magnet = message.data["uri"]

        self.show_gui("Launching peerflix")
        self.stop_peerflix()
        self.running = True
        url = None
        buffered_enough = False
        out_logs = []
        self.peerflix = pexpect.spawn('peerflix ' + magnet)
        while self.running:
            try:
                out = self.peerflix.readline().decode("utf-8").strip()
                if out and out not in out_logs:
                    LOG.info(out)
                    out_logs.append(out)
                if not url and "http:" in out:
                    url = out.split("http://")[-1].split("/")[0]
                    LOG.debug(f"Stream url: {url}")
                    message.data["uri"] = "http://" + url
                    message.data["playback"] = PlaybackType.VIDEO
                elif "info" in out:
                    if url and not buffered_enough:
                        if "%" in out:
                            n = int(out.split("%")[0].split("(")[-1])
                            self.show_gui(f"Buffering: {n}%")
                            if n >= self.settings["min_buffer_percent"]:
                                buffered_enough = True
                                self.ocp_play(message)
                elif "Verifying downloaded:" in out:
                    n = int(out.split("%")[0].split(" ")[-1])
                    self.show_gui(f"Verifying downloaded: {n}%")
            except pexpect.exceptions.EOF:
                # peerflix exited
                LOG.info("Peerflix exited")
                self.running = False
            except pexpect.exceptions.TIMEOUT:
                # nothing happened for a while
                LOG.warning("Peerflix stalled!")
            except Exception as e:
                LOG.exception(e)
                self.running = False


def create_skill():
    return PeerflixSkill()
