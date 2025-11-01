"""
FastAPI Service for GitLab API Integration
Exposes endpoints to interact with GitLab API functions

Run 
  uv run --env-file=.env app.py
"""

from fastapi import FastAPI, HTTPException, Request
import os
from datetime import datetime
import requests 
import gitlab_calls


app = FastAPI(
    title="GitLab API Service",
    description="Service for managing GitLab user permissions and querying issues/merge requests",
    version="1.0.0"
)



@app.get("/")
async def list_endpoints(request: Request):
    '''
      Displays endpoints
    '''
    # Extract all route paths and their HTTP methods
    endpoints = [
        {"path": route.path, "name": route.name, "methods": list(route.methods)}
        for route in request.app.routes
    ]
    return {"endpoints": endpoints}

@app.post("/grant-role")
async def grant_role(request: Request):
    """
    Grant or change role permissions for a user on a repository or group.
    
    Expected JSON body:
    {
        "username": "john.doe",
        "repo_or_group": "mygroup/myproject",
        "role": "developer"
    }
    """
    try:
        body = await request.json()
        
        username = body.get('username')
        repo_or_group = body.get('repo_or_group')
        role = body.get('role')
        
        result = gitlab_calls.grant_user_role(
            username=username,
            repo_or_group=repo_or_group,
            role=role
        )
        
        return {
            "success": True,
            "message": f"Successfully granted '{role}' role to user '{username}'",
            "data": result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/get-items")
async def get_items(request: Request):
    """
    Retrieve all merge requests or issues created in a given year.
    
    Expected JSON body:
    {
        "item_type": "mr",
        "year": 2023
    }
    """
    try:
        body = await request.json()
        
        item_type = body.get('item_type')
        year = body.get('year')
        
        items = gitlab_calls.get_items_by_year(
            item_type=item_type,
            year=year
        )
        
        return {
            "success": True,
            "count": len(items),
            "items": items
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def main():
    '''
    Bogus entrypoint - for debug
    '''
    print("Hello from mobileye-home-assignment!")

    print(gitlab_calls.get_items_by_year('issues',2025))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


 