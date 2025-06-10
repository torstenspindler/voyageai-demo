db = db.getSiblingDB("mercadona");

const index = {
  name: "vo_vector_index",
  type: "vectorSearch",
  definition: {
    fields: [
      {
        numDimensions: 1024,
        path: "vo_embedding",
        similarity: "cosine",
        type: "vector",
      },
    ],
  },
};

// Create the index
db.products.createSearchIndex(index);
print(`Search index "${index.name}" has been created.`);