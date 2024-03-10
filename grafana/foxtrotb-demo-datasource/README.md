# Running in dev mode

1. Build frontend

```
yarn
yarn dev
```

2. Build backend

```
./redeploy.dev.sh
```

And then in `custom_datasource` container

```
./run.sh
```

This should create and put `gpx_demo_datasource_linux_amd64` to `grafana/foxtrotb-demo-datasource/dist`

3. Run grafana with plugin built in dist

```
./redeploy.dev.sh

```
