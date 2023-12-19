# import graphene
# from flask import Flask
# from flask_graphql import GraphQLView
# import requests

import strawberry

from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
import requests

recipeURL = "http://ec2-54-91-9-29.compute-1.amazonaws.com:8011"
reviewURL = "http://review-management-402504.ue.r.appspot.com"

class Review(strawberry.ObjectType):
    # necessary info 
    review_id = strawberry.ID(required=True)
    recipe_id = strawberry.ID(required=True)
    user_id = strawberry.ID(required=True)

    date = strawberry.DateTime()
    rating = strawberry.Float()
    text = strawberry.String()
    upvotes = strawberry.Int()
    downvotes = strawberry.Int()

    # get the title associated with the review 
    def resolve_recipe_title(self, info):
        response = requests.get(f"{recipeURL}/recipes/{self.recipe_id}")
        if response.status_code == 200:
            recipe_data = response.json()
            print('recipe_data', recipe_data)
            return recipe_data.get("title")  # need to check on the way to extract title
        else:
            return None

class Recipe(strawberry.ObjectType):
    recipe_id = strawberry.ID(required=True)
    title = strawberry.String(required=True)
    author_id = strawberry.ID(required=True)

    ingredients = strawberry.List(strawberry.String)
    steps = strawberry.List(strawberry.String)
    images = strawberry.List(strawberry.String)


# this is the root query type
# all top level read oeprations defined here
class Query(strawberry.ObjectType):
    # returns a list of review objects and gets user_id for each
    # client can query user reviews
    # by providing user_id, will generate a list of review written by the user
    user_reviews = strawberry.List(Review, user_id=strawberry.ID(required=True))
    print(user_reviews)

    # creates a recipe field in the schema
    # returns a single recipe object when provided with recipe_id
    recipe = strawberry.Field(Recipe, recipe_id=strawberry.ID(required=True)) 
    
    # creates a recipe review field 
    # returns a single review object when provided with review_id
    review = strawberry.Field(Review, review_id=strawberry.ID(required=True))

    # fetches and returns list of reviews for a specified user
    def resolve_user_reviews(self, info, user_id):
        # get the reviews from microservice
        response = requests.get(f"{reviewURL}/reviews/{user_id}")
        if response.status_code == 200:
            data = response.json()
            print('resolve user reviews', data)
            return data # Assuming the response is a list of reviews
        else:
            return []  # Handle errors appropriately
    
    def resolve_recipe(self, info, recipe_id):
        # fetch data for a specific recipe 
        response = requests.get(f"{recipeURL}/recipes/{recipe_id}")
        if response.status_code == 200:
            return response.json() 
        else:
            return None
    
    # fetches data for a specific review based on review_id
    def resolve_review(self, info, review_id):
        response = requests.get(f"{reviewURL}/reviews/{review_id}")
        if response.status_code == 200:
            return response.json()
        else:
            return None


# schema = graphene.Schema(query=Query)

# app = Flask(__name__)
# app.add_url_rule(
#     '/graphql',
#     view_func=GraphQLView.as_view(
#         'graphql',
#         schema=schema,
#         graphiql=True 
#     )
# )
        
schema = strawberry.Schema(Query)

graphql_app = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")

if __name__ == '__main__':
    app.run()
