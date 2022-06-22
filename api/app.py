import os
from flask import Flask, abort, render_template, request, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pytz import timezone
from collections import deque, defaultdict

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] =\
    "sqlite:///" + os.path.join(basedir, "products.db")

# If set to True, Flask-SQLAlchemy will track modifications of objects and emit signals.
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# connect Flask application with SQLAlchemy
db = SQLAlchemy(app)


class Element(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parentId = db.Column(db.Integer)
    name_of_element = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Integer)
    # timezone = True enables timezone support.
    # default with a scalar or Python function directly produces a Python default value,
    # then sends the new value to the server when inserting.
    # If you have multiple clients on different platforms accessing the same database,
    # a server_default ensures that all clients will use the same defaults.
    date = db.Column(
        db.DateTime(timezone=True),
        default=datetime.now(tz=timezone("Europe/Moscow"))
    )

    # Now - creation date attribute is a datetime object and
    # doesn't give you any specific representation per se.
    # Instead, it contain some methods (like __str__, __repr__, isoformat, etc.)
    # that helps you get desired representation of datetime object.
    def __repr__(self):
        return f"{self.id} - {self.parentId} - {self.name_of_element} - {self.price} - {self.date.isoformat()}"


@app.route("/home")
@app.route("/")
def index() -> str:
    """The home page.

    Args:

    Returns:
        The home page template.
    """
    return render_template("index.html")


def error_400() -> None:
    """Stops execution with abort(400) at the place where it is called.

    Args:

    Returns:
        400 error.
    """
    abort(
            make_response({"code": 400, "message": "Validation Failed"}, 400),
            description="Невалидная схема документа или входные данные не верны."
        )


def error_404() -> None:
    """Stops execution with abort(404) at the place where it is called.

    Args:

    Returns:
        None.
    """
    abort(
            make_response({"code": 404, "message": "Item not found"}, 404),
            description="Категория/товар не найден."
        )


def is_there_id_in_table(id: str) -> int:
    """Checks if there is an id in the table.

    Args:
        id: the id of the record in the table.

    Returns:
        If successful, it returns the id.
    """
    try:
        id = int(id)
        if Element.query.get(id) is None:
            raise ValueError
    except ValueError:
        error_404()

    return id


@app.route("/imports", methods=["GET", "POST"])
def imports() -> (str, dict):
    """Adds or modifies records to the table.

    Args:

    Returns:
        Returns imports template if the GET method is used,
        otherwise, if successful, it redirects to the home page.
    """
    if request.method == "GET":
        return render_template("imports.html")

    id = request.form["id"]
    if id:
        id = is_there_id_in_table(id)

    try:
        parentId = int(request.form["parentId"])
        if Element.query.get(parentId) is None:
            error_404()
    except ValueError:
        parentId = None

    name_of_element = request.form["name_of_element"]
    if not name_of_element:
        error_400()

    price = request.form["price"]
    try:
        price = int(request.form["price"])
        if price < 0:
            error_400()
    except ValueError:
        price = None

    if id:
        element = Element.query.get(id)
        element.parentId = parentId
        element.name_of_element = name_of_element
        element.price = price
        element.date = datetime.now(tz=timezone("Europe/Moscow"))
    else:
        db.session.add(Element(parentId=parentId, name_of_element=name_of_element, price=price))
        db.session.commit()

    # the Flask 200 default, the standard code for a successfully handled request
    return render_template("success_page.html"), {"Refresh": "3; url=/home"}


def search_and_delete(id: str) -> None:
    """Deletes a record and all child records in the table by id.

    Args:
        id: the id of the record in the table.

    Returns:
        If successful, it redirects to the home page.
    """
    id = is_there_id_in_table(id)

    deq = deque([id])
    while deq:
        id_to_delete = deq.popleft()
        for son in Element.query.filter_by(parentId=id_to_delete):
            deq.append(son.id)

        u = db.session.get(Element, id_to_delete)
        db.session.delete(u)
        db.session.commit()


@app.route("/delete", methods=["GET", "POST"])
def delete() -> (str, dict):
    """Deletes a record and all child records in the table by id.

    Args:

    Returns:
        Returns delete template if the GET method is used,
        otherwise, if successful, it redirects to the home page.
    """
    if request.method == "GET":
        return render_template("delete.html")

    id = request.form["id"]
    search_and_delete(id)

    return render_template("success_page.html"), {"Refresh": "3; url=/home"}


@app.route("/delete/<id>")
def delete_by_id(id: str) -> (str, dict):
    """Deletes a record and all child records in the table by id.

    Args:
        id: the id of the record in the table.

    Returns:
        If successful, it redirects to the home page.
    """
    search_and_delete(id)

    return render_template("success_page.html"), {"Refresh": "3; url=/home"}


def create_dicts_with_prices_and_adjacency_lists(id: str) -> (int, dict, defaultdict, set):
    """Creates adjacency lists by id and parentID and
    also a dictionary "prices" with pairs {id: initial price}.
    Finds all IDs related to the category.

    Args:
        id: the id of the record in the table.

    Returns:
        If successful, returns the original ID,
        dictionaries with prices and adjacency lists.
        Also, a set with ids.
    """
    id = is_there_id_in_table(id)

    prices = {id: Element.query.get(id).price}
    deq = deque([id])
    parents_and_children_id = defaultdict(list)
    all_ids = {id}
    while deq:
        parent_id = deq.popleft()
        for son in Element.query.filter_by(parentId=parent_id):
            prices[son.id] = son.price
            deq.append(son.id)
            parents_and_children_id[parent_id].append(son.id)
            all_ids.add(son.id)

    return id, prices, parents_and_children_id, all_ids


def find_price_for_each_id(id: int, prices: dict, adjacency_list: defaultdict) -> (int, int):
    """Recalculates prices taking into account the ID of children.
    The function works according to the DFS algorithm.

        Args:
            id: the id of the record in the table.
            prices: the ID of the table elements and their corresponding prices.
            adjacency_list: parents and their children with appropriate ids.

        Returns:
            The price of the item in question and
            the quantity of goods to the current moment.
        """
    price_of_element = 0 if prices[id] is None else prices[id]
    num_of_products = 0 if prices[id] is None else 1
    for son_id in adjacency_list[id]:
        price_and_quantity = find_price_for_each_id(son_id, prices, adjacency_list)
        price_of_element += price_and_quantity[0]
        num_of_products += price_and_quantity[1]

    if prices[id] is None and num_of_products:
        prices[id] = price_of_element / num_of_products

    return price_of_element, num_of_products


@app.route("/nodes", methods=["GET", "POST"])
def nodes() -> str:
    """Provides information about an element by id.
    When getting information about a category,
    information about its child elements is also provided.

        Args:

        Returns:
            Returns nodes template if the GET method is used,
            otherwise, if successful, it returns info_by_id template with
            information about the elements.
        """
    if request.method == "GET":
        return render_template("nodes.html")

    id = request.form["id"]
    id, prices, parents_and_children_id, all_ids = create_dicts_with_prices_and_adjacency_lists(id)
    find_price_for_each_id(id, prices, parents_and_children_id)

    return render_template("info_by_id.html", elements=Element.query.filter(Element.id.in_(all_ids)).all())


@app.route("/nodes/<id>")
def nodes_by_id(id: str) -> str:
    """Provides information about an element by id.
    When getting information about a category,
    information about its child elements is also provided.

        Args:
            id: the id of the record in the table.

        Returns:
            If successful, it returns info_by_id template with
            information about the elements.
        """
    id, prices, parents_and_children_id, all_ids = create_dicts_with_prices_and_adjacency_lists(id)
    find_price_for_each_id(id, prices, parents_and_children_id)

    return render_template("info_by_id.html", elements=Element.query.filter(Element.id.in_(all_ids)).all())
