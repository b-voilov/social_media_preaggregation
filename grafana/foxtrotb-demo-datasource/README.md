# Running in dev mode

1. Run compose

```
./redeploy.dev.sh
```

2. Build frontend
   In frontend container, `/app` directory

```
yarn
yarn dev
```

3. Build backend
   In `custom_datasource` container

```
./run.sh
```

This should create and put `gpx_demo_datasource_linux_amd64` to `grafana/foxtrotb-demo-datasource/dist`

3. Run grafana with plugin built in dist

```
./redeploy.dev.sh

```
