import numpy as np
import faiss
from langchain_openai import OpenAIEmbeddings
from decouple import config
import os
import requests
import logging


#load the OpenAI API key
openai_api_key = config('OPENAI_API_KEY')

os.environ["OPENAI_API_KEY"] = openai_api_key

class VectorDBService:
    def __init__(self):
        self.embedder = OpenAIEmbeddings()
        self.index = None
        self.products = self._fetch_products()
        self._create_faiss_index()

    def _fetch_products(self):
        """Fetch products from the Fake Store API."""
        try:
            response = requests.get("https://fakestoreapi.com/products")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Error fetching products: {str(e)}")
            return []

    def _create_faiss_index(self):
        """Create a FAISS index from product descriptions."""
        if not self.products:
            return None
        product_embeddings = [
            f"{product['title']} {product['description']} {product['category']} "
            f"Price: {product['price']} ID: {product['id']} "
            f"Rating: {product['rating']['rate']} (based on {product['rating']['count']} reviews)"
            for product in self.products
        ]
        embeddings_array = np.array(self.embedder.embed_documents(product_embeddings))
        self.index = faiss.IndexFlatL2(embeddings_array.shape[1])
        self.index.add(embeddings_array)
        return self.index

    def search_products(self, query: str, top_k: int = 10, max_distance: float = 1.5):
        """
        Search products with enhanced matching and error handling.
        Returns: {
            'products': list of matched products,
            'distances': corresponding similarity distances,
            'error': optional error message
        }
        """

        if not self.index or not self.products:

            return {'error': 'Product not available'}

        try:
            # Convert query to embedding
            query_embedding = np.array(self.embedder.embed_documents([query]))

            # Search with distance thresholds
            distances, indices = self.index.search(query_embedding, top_k)

            # Filter results by distance and validity
            valid_results = []
            valid_distances = []
            for i, distance in zip(indices[0], distances[0]):
                
                if i < len(self.products) and distance <= max_distance:
                    valid_results.append(self.products[i])
                    valid_distances.append(distance)

            if not valid_results:
                return {'error': 'No matching products found. Please try different search terms.'}

            return {
                'products': valid_results,
                'distances': valid_distances
            }

        except Exception as e:
            logging.error(f"Search error: {str(e)}")
            return {'error': 'Failed to process search request'}

