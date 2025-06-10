# Database setup

This document describes the needed database setup

## Restore Database dump

The Database directory contains a dump for the mercadona database which is needed.
During mongorestore we need to rename this database to mercasmart (--nsFrom, --nsTo arguments).

Example for restoring from dump directory into a mongod running on localhost without authentication:

`mongorestore --gzip --nsFrom mercadona.\* --nsTo mercasmart.\*`

## Index Definitions needed

Three indices for Vector Search on mercasmart.Products are needed:

They can easily be defined via the Atlas Search Index Web UI.

vo_vector_index and vo_image_index are needed for VoyageAI
vector_index is needed for openAI

vo_vector_index:
```json
{
    "fields": [
      {
        "numDimensions": 1024,
        "path": "vo_embedding",
        "similarity": "cosine",
        "type": "vector"
      }
    ]
}
```

vo_image_index:
```json
{
  "fields": [
    {
      "numDimensions": 1024,
      "path": "vo_img_embedding",
      "similarity": "euclidean",
      "type": "vector"
    }
  ]
}
```

vector_index:
```json
{
  "fields": [
    {
      "numDimensions": 1536,
      "path": "embedding",
      "similarity": "euclidean",
      "type": "vector"
    }
  ]
}
```
