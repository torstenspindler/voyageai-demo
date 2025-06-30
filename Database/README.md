# Database setup

This document describes the needed database setup

## Restore Database dump

The Database directory contains the files from the dump for the mercadona database which is needed.

### Download dumps

- [mercasmsart.dump](https://localhost/mercassmart.dump)

The file is gzipped archive of the database and can be restored for example to localhost via:

`mongorestore --drop --gzip --archive=mercasmart.dump`

You can find the proper URL to use for your Atlas cluster from the Atlas Tools dialog.

## Index Definitions needed

Three indices for Vector Search on *mercasmart.Products* are needed:

They can easily be defined via the Atlas Search Index Web UI.

**vo_vector_index** and **vo_image_index** are needed for VoyageAI
**vector_index** is needed for openAI

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
