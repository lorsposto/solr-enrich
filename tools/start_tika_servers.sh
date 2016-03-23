#!/usr/bin/env bash

echo 'java -classpath location-ner-model:geotopic-mime:tika-server-1.12.jar org.apache.tika.server.TikaServerCli --port 9980'
nohup java -classpath location-ner-model:geotopic-mime:tika-server-1.12.jar org.apache.tika.server.TikaServerCli --port 9980 > logs/9980.log 2>&1 &

echo 'java -classpath location-ner-model:geotopic-mime:tika-server-1.12.jar org.apache.tika.server.TikaServerCli --port 9981'
nohup java -classpath location-ner-model:geotopic-mime:tika-server-1.12.jar org.apache.tika.server.TikaServerCli --port 9981 > logs/9981.log 2>&1 &

echo 'java -classpath location-ner-model:geotopic-mime:tika-server-1.12.jar org.apache.tika.server.TikaServerCli --port 9982'
nohup java -classpath location-ner-model:geotopic-mime:tika-server-1.12.jar org.apache.tika.server.TikaServerCli --port 9982 > logs/9982.log 2>&1 &

echo 'java -classpath location-ner-model:geotopic-mime:tika-server-1.12.jar org.apache.tika.server.TikaServerCli --port 9983'
nohup java -classpath location-ner-model:geotopic-mime:tika-server-1.12.jar org.apache.tika.server.TikaServerCli --port 9983 > logs/9983.log 2>&1 &

echo 'java -classpath location-ner-model:geotopic-mime:tika-server-1.12.jar org.apache.tika.server.TikaServerCli --port 9984'
nohup java -classpath location-ner-model:geotopic-mime:tika-server-1.12.jar org.apache.tika.server.TikaServerCli --port 9984 > logs/9984.log 2>&1 &

echo 'java -classpath location-ner-model:geotopic-mime:tika-server-1.12.jar org.apache.tika.server.TikaServerCli --port 9985'
nohup java -classpath location-ner-model:geotopic-mime:tika-server-1.12.jar org.apache.tika.server.TikaServerCli --port 9985 > logs/9985.log 2>&1 &

# nohup python geo_enrich.py --tika http://localhost:9980/tika --start 0 --rows 1000 --rounds 100 > logs/9980.log 2>&1 &
# nohup python geo_enrich.py --tika http://localhost:9981/tika --start 100000 --rows 1000 --rounds 100 > logs/9981.log &
# nohup python geo_enrich.py --tika http://localhost:9982/tika --start 200000 --rows 1000 --rounds 100 > logs/9982.log &
# nohup python geo_enrich.py --tika http://localhost:9983/tika --start 300000 --rows 1000 --rounds 100 > logs/9983.log &
# nohup python geo_enrich.py --tika http://localhost:9984/tika --start 400000 --rows 1000 --rounds 100 > logs/9984.log &
# nohup python geo_enrich.py --tika http://localhost:9985/tika --start 500000 --rows 1000 --rounds 100 > logs/9985.log &

# curl http://polar.usc.edu/solr/geo_enrich/update --data '<delete><query>*:*</query></delete>' -H 'Content-type:text/xml; charset=utf-8'

# curl http://polar.usc.edu/solr/geo_enrich/update --data '<commit/>' -H 'Content-type:text/xml; charset=utf-8'