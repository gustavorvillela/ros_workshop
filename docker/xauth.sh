#!/bin/bash

# Remove existing X11 auth files
rm -rf /tmp/.docker.xauth

# Create new X11 auth
touch /tmp/.docker.xauth
xauth nlist $DISPLAY | sed -e 's/^..../ffff/' | xauth -f /tmp/.docker.xauth nmerge -

# Set proper permissions
chmod 644 /tmp/.docker.xauth