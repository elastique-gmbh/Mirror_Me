# Mirror Me
Interactive kinetic installation exploring self-perception through cobot-controlled mirrors and immersive soundscapes.

Mirror Me is an immersive kinetic installation that delves into themes of radical self-expression and digital identity. Developed by Elastique. GmbH, the project features two collaborative robots (cobots) manipulating mirrored surfaces to create endless visual "echoes" of the viewer. Accompanied by four distinct soundscapes, the installation transforms into a hyper-charged echo chamber of the self.

In an era dominated by self-referential digital content, Mirror Me invites participants to reflect—both literally and metaphorically—on their presence and perception. The synchronized movements of the mirrors and the evolving soundscapes create an environment that is both introspective and expressive. Visitors become central to the artwork, experiencing a continuous loop of self-observation and expression.

Video-Documentation:
https://vimeo.com/elastique/mirrorme

# Technical Overview

Robotics: Utilizes two Universal Robots cobots to maneuver mirrored panels in choreographed sequences.

Animation & Control: Robot movements are designed in Cinema 4D, with animation data extracted and processed via Python scripts. This data is then integrated into TouchDesigner to trigger real-time interactions.

Sound Design: Four unique soundscapes correspond to different movement sequences, each eliciting varied emotional responses—from light and floating to aggressive and oppressive. Created in Pro Tools using Plugins from Native Instruments, Waves and more

Visitor Interaction: An automated system captures and edits a video of each visitor's experience from three angles, available for download 20 seconds post-interaction. This feature encourages sharing and re-engagement, reinforcing the theme of self-reflection.

# Network
Network performance between the PC running Mirror-Me Player and the Bots is extremely important. The Bots and the Laptop should be connected by a Gigabit-Switch. Please do not use LTE-Routers or similar devices with integrated switches for connecting the Bots to the PC.

- IP-Network: 10.100.0.0/24
- 4G Router IP: 10.100.0.1
- Laptop: 10.100.0.120
- Bot A: 10.100.0.125
- Bot B: 10.100.0.126
- Cam A: 10.100.0.110
- Cam B: 10.100.0.111
- Cam C: 10.100.0.111
