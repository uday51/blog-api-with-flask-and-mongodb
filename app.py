from flask import Flask,jsonify,request
from pymongo import MongoClient
from bson.objectid import ObjectId

app=Flask(__name__)
client=MongoClient("mongodb://localhost:27017")
db=client["blog"]
collection=db["blogs"]

@app.route("/posts",methods=["POST"])
def add_post():
    data=request.json
    post_id=collection.insert_one({
        "title":data["title"],
        "content": data["content"],
        "author": data["author"],
        "comments": [],
        "likes": 0,

    }).inserted_id
    return jsonify({"msg":"Posted successfully","Post_id":str(post_id)})

@app.route('/post/<post_id>',methods=["GET"])
def get_specific_post(post_id):
    post=collection.find_one({"_id":ObjectId(post_id)})
    if post:
        return jsonify({
            "title":post["title"],
            "content":post["content"],
            "author":post["author"],
            "comments":post["comments"],
            "likes":post["likes"]
        })
    return jsonify({"msg":"Post not found"})


@app.route('/add-comment/<post_id>',methods=["POST"])
def add_comment(post_id):
    data=request.json
    print(data)
    comments={"user":data["user"],"comment":data["comment"]}
    result=collection.update_one({"_id":ObjectId(post_id)},{"$push":{"comments":comments}})
    if result.matched_count:
        return jsonify({"msg":"comment added"})
    return jsonify({"msg":"Blog post not found"})

@app.route('/like/<post_id>',methods=["POST"])
def add_like(post_id):
    result=collection.update_one({"_id":ObjectId(post_id)},{"$inc":{"likes":1}})
    if result.matched_count:
        return jsonify({"msg":"like added"})
    return jsonify({"msg":"post not found"})

@app.route('/delete/<post_id>',methods=["DELETE"])
def delete_post(post_id):
    data=request.json
    post=collection.find_one({"_id":ObjectId(post_id)})
    if post:
        if data["author"]== post["author"]:
            collection.delete_one({"_id":ObjectId(post_id)})
            return jsonify({"msg":"post deleted"})
        return jsonify({"msg":"no permission"})
    return jsonify({"msg":"blog not found"})

@app.route('/posts',methods=["GET"])
def get_all_posts():
    pages=int(request.args.get("page",1))
    limit=int(request.args.get("limit",5))
    skip=(pages-1)*limit
    posts=[]
    for post in collection.find().skip(skip).limit(limit):
        posts.append({
            "id":str(post["_id"]),
            "title":post["title"],
            "content":post["content"],
            "author":post["author"],
            "comments":post["comments"],
            "likes":post["likes"]

        })

    return jsonify(posts)




if __name__=="__main__":
    app.run(debug=True)
