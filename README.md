# Build

```
docker build -t catmonitor -f Dockerfile.pi .
```

# Run

Change device and data directory accordingly.

```
docker run --device=/dev/video0 -v /home/pi/Development/git/catmonitor.py/data:/data catmonitor
```
