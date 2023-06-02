FROM overv/openstreetmap-tile-server

COPY ./extracts/missouri_et_al.osm.pbf /data/region.osm.pbf
VOLUME osm-data:/data/database/
VOLUME osm-tiles:/data/tiles/

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
RUN /entrypoint.sh