#!/usr/bin/env python3
from setuptools import setup

# skill_id=package_name:SkillClass
PLUGIN_ENTRY_POINT = 'skill-peerflix.jarbasai=skill_peerflix:PeerflixSkill'

setup(
    # this is the package name that goes on pip
    name='ovos-skill-peerflix',
    version='0.0.1',
    description='ovos peerflix skill plugin',
    url='https://github.com/JarbasSkills/skill-peerflix',
    author='JarbasAi',
    author_email='jarbasai@mailfence.com',
    license='Apache-2.0',
    package_dir={"skill_peerflix": ""},
    package_data={'skill_peerflix': ['locale/*', 'ui/*']},
    packages=['skill_peerflix'],
    include_package_data=True,
    install_requires=["ovos_workshop~=0.0.5a1"],
    keywords='ovos skill plugin',
    entry_points={'ovos.plugin.skill': PLUGIN_ENTRY_POINT}
)
