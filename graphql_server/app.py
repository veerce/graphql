import strawberry
import requests
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

recipeURL = "http://ec2-18-209-24-141.compute-1.amazonaws.com:8011"
reviewURL = "http://review-management-402504.ue.r.appspot.com"

@strawberry.type
class Review:
    # necessary info 
    review_id: strawberry.ID
    recipe_id: strawberry.ID
    user_id: strawberry.ID

    date: str
    rating: float
    text: str
    upvotes: int
    downvotes: int

    # get the title associated with the review 
    @strawberry.field
    def recipe_title(self) -> str:
        response = requests.get(f"{recipeURL}/recipes/{self.recipe_id}")
        if response.status_code == 200:
            recipe_data = response.json()
            if recipe_data is not None:
                return recipe_data.get("title")
            else:
                return "Unknown Title"  # Or any other placeholder text
        else:
            return "Error Fetching Title"  # Indicate that an error occurred


@strawberry.type
class Recipe:
    recipe_id: strawberry.ID
    title: str
    author_id: strawberry.ID
    ingredients: str
    steps: str
    images: str

# this is the root query type
# all top level read oeprations defined here
@strawberry.type
class Query:
    # get the reviews from microservice associated with a user
    @strawberry.field
    def user_reviews(self, user_id: strawberry.ID) -> list[Review]:
        response = requests.get(f"{reviewURL}/user/{user_id}")
        if response.status_code == 200:
            review_tuples = response.json()  # Assuming this returns a list of tuples
            print('review tuples', review_tuples)
            # Map the tuple data to Review instances
            reviews = [
                Review(
                    review_id=str(review_tuple[0]),
                    recipe_id=str(review_tuple[1]),
                    user_id=str(review_tuple[2]),
                    date=str(review_tuple[3]),
                    rating=str(review_tuple[4]),
                    text=str(review_tuple[5]),
                    upvotes=str(review_tuple[6]),
                    downvotes=str(review_tuple[7])
                )
                for review_tuple in review_tuples
            ]
            return reviews
        else:
            return []

    # fetch data for a specific recipe 
    @strawberry.field
    def recipe(self, recipe_id: strawberry.ID) -> Recipe:
        response = requests.get(f"{recipeURL}/recipes/{recipe_id}")
        if response.status_code == 200:
            data = response.json()
            print('data', data)
            return data
        else:
            return None

    # fetches data for a specific review based on review_id
    @strawberry.field
    def review(self, review_id: strawberry.ID) -> Review:
        response = requests.get(f"{reviewURL}/reviews/{review_id}")
        if response.status_code == 200:
            review_tuple = response.json()  # Assuming this returns a tuple
            print('review tuple', review_tuple)
            return Review(
                review_id=str(review_tuple[0]),
                recipe_id=str(review_tuple[1]),
                user_id=str(review_tuple[2]),
                date=str(review_tuple[3]),
                rating=str(review_tuple[4]),
                text=str(review_tuple[5]),
                upvotes=str(review_tuple[6]),
                downvotes=str(review_tuple[7])
            )
        else:
            return None


schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema, graphiql=True)
app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")

origins = [
    "http://localhost:3000",  # Assuming the frontend runs on localhost:3000
    "http://127.0.0.1:3000",   # Include this if you access the frontend via 127.0.0.1
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)