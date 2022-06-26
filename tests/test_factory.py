# Use only
# python -m pytest tests
# command because
# https://docs.pytest.org/en/latest/explanation/pythonpath.html#invoking-pytest-versus-python-m-pytest


import pytest
from api.app import Element


@pytest.mark.parametrize(
    "page",
    [
        "/",
        "/home",
        "/imports",
        "/nodes",
        "/delete",
    ]
)
def test_page_status(flask_app, page):
    response = flask_app.get(page)
    assert response.status_code == 200


@pytest.mark.parametrize(
    "page, correct_response",
    [
        ("/",        b"Home page"),
        ("/home",    b"Home page"),
        ("/imports", b"Imports"),
        ("/nodes",   b"Nodes"),
        ("/delete",  b"Deletes an element by ID"),
    ]
)
def test_page_response(flask_app, page, correct_response):
    response = flask_app.get(page)
    assert correct_response in response.data


def test_import_one_product_without_category_and_its_status(flask_app, empty_db):
    response = flask_app.post("/imports", data={
        "id": '',
        "parentId": '',
        "name_of_element": "Opple watch",
        "price": 5,
    })

    assert response.status_code == 200


def test_import_one_product_without_category_and_its_presence_in_the_database():
    elem = Element.query.get(1)
    assert elem.id == 1 and \
           elem.parentId is None and \
           elem.name_of_element == "Opple watch" and \
           elem.price == 5


def test_node_one_product_without_category_and_its_status(flask_app):
    response = flask_app.post("/nodes", data={
        "id": 1,
    })

    assert response.status_code == 200


def test_node_one_product_without_category_and_its_values(flask_app):
    response = flask_app.post("/nodes", data={
        "id": 1,
    })

    response_data = response.data
    for field in (
        b"<p><b>id</b> = 1</p>",
        b"<p><b>ParentId</b> = None</p>",
        b"<p><b>The name of the element</b>: Opple watch</p>",
        b"<p><b>Price</b>: 5</p>"
    ):
        assert field in response_data


def test_node_one_product_without_category_and_its_values_with_different_path(flask_app):
    response = flask_app.get("/nodes/1")

    response_data = response.data
    for field in (
            b"<p><b>id</b> = 1</p>",
            b"<p><b>ParentId</b> = None</p>",
            b"<p><b>The name of the element</b>: Opple watch</p>",
            b"<p><b>Price</b>: 5</p>"
    ):
        assert field in response_data


def test_delete_one_product_without_category_and_its_status(flask_app):
    response = flask_app.get("/delete/1")

    assert response.status_code == 200


def test_check_that_product_without_category_is_not_available(flask_app):
    response = flask_app.get("/delete/1")

    assert response.json["code"] == 404 and response.json["message"] == "Item not found"


def test_check_that_product_without_category_has_been_removed_from_database(flask_app):
    elem = Element.query.get(1)

    assert elem is None





def test_import_one_category_without_parent_and_its_status(flask_app, empty_db):
    response = flask_app.post("/imports", data={
        "id": '',
        "parentId": '',
        "name_of_element": "Watches",
        "price": '',
    })

    assert response.status_code == 200


def test_import_one_category_without_parent_and_its_presence_in_the_database():
    elem = Element.query.get(1)
    assert elem.id == 1 and \
           elem.parentId is None and \
           elem.name_of_element == "Watches" and \
           elem.price is None


def test_node_one_category_without_parent_and_its_status(flask_app):
    response = flask_app.post("/nodes", data={
        "id": 1,
    })

    assert response.status_code == 200


def test_node_one_category_without_parent_and_its_values(flask_app):
    response = flask_app.post("/nodes", data={
        "id": 1,
    })

    response_data = response.data
    for field in (
        b"<p><b>id</b> = 1</p>",
        b"<p><b>ParentId</b> = None</p>",
        b"<p><b>The name of the element</b>: Watches</p>",
        b"<p><b>Price</b>: None</p>"
    ):
        assert field in response_data


def test_node_one_category_without_parent_and_its_values_with_different_path(flask_app):
    response = flask_app.get("/nodes/1")

    response_data = response.data
    for field in (
            b"<p><b>id</b> = 1</p>",
            b"<p><b>ParentId</b> = None</p>",
            b"<p><b>The name of the element</b>: Watches</p>",
            b"<p><b>Price</b>: None</p>"
    ):
        assert field in response_data


def test_delete_one_category_without_parent_and_its_status(flask_app):
    response = flask_app.get("/delete/1")

    assert response.status_code == 200


def test_check_that_category_without_parent_is_not_available(flask_app):
    response = flask_app.get("/delete/1")

    assert response.json["code"] == 404 and response.json["message"] == "Item not found"


def test_check_that_category_without_parent_has_been_removed_from_database(flask_app):
    elem = Element.query.get(1)

    assert elem is None





def test_import_one_product_and_its_category(flask_app, empty_db):
    response1 = flask_app.post("/imports", data={
        "id": '',
        "parentId": '',
        "name_of_element": "Watches",
        "price": '',
    })

    response2 = flask_app.post("/imports", data={
        "id": '',
        "parentId": 1,
        "name_of_element": "Opple watch",
        "price": 5,
    })

    assert response1.status_code == response2.status_code == 200


def test_import_one_product_and_its_category_and_their_presence_in_the_database():
    category = Element.query.get(1)
    assert category.id == 1 and \
           category.parentId is None and \
           category.name_of_element == "Watches" and \
           category.price is None

    product = Element.query.get(2)
    assert product.id == 2 and \
           product.parentId == 1 and \
           product.name_of_element == "Opple watch" and \
           product.price == 5


def test_node_one_product_and_its_category(flask_app):
    response1 = flask_app.post("/nodes", data={
        "id": 1,
    })

    response2 = flask_app.post("/nodes", data={
        "id": 2,
    })

    assert response1.status_code == response2.status_code == 200


def test_node_one_product_and_its_category_and_their_values(flask_app):
    response1 = flask_app.post("/nodes", data={
        "id": 1,
    })

    response1_data = response1.data
    for field in (
        b"<p><b>id</b> = 1</p>",
        b"<p><b>ParentId</b> = None</p>",
        b"<p><b>The name of the element</b>: Watches</p>",
        b"<p><b>Price</b>: None</p>"
    ):
        assert field in response1_data

    response2 = flask_app.post("/nodes", data={
        "id": 2,
    })

    response2_data = response2.data
    for field in (
        b"<p><b>id</b> = 2</p>",
        b"<p><b>ParentId</b> = 1</p>",
        b"<p><b>The name of the element</b>: Opple watch</p>",
        b"<p><b>Price</b>: 5</p>"
    ):
        assert field in response2_data


def test_node_one_product_and_its_category_and_their_values_with_different_path(flask_app):
    response1 = flask_app.get("/nodes/1")

    response1_data = response1.data
    for field in (
        b"<p><b>id</b> = 1</p>",
        b"<p><b>ParentId</b> = None</p>",
        b"<p><b>The name of the element</b>: Watches</p>",
        b"<p><b>Price</b>: None</p>"
    ):
        assert field in response1_data

    response2 = flask_app.get("/nodes/2")

    response2_data = response2.data
    for field in (
        b"<p><b>id</b> = 2</p>",
        b"<p><b>ParentId</b> = 1</p>",
        b"<p><b>The name of the element</b>: Opple watch</p>",
        b"<p><b>Price</b>: 5</p>"
    ):
        assert field in response2_data


def test_delete_one_product_and_its_category(flask_app):
    response2 = flask_app.get("/delete/2")
    response1 = flask_app.get("/delete/1")

    assert response2.status_code == response1.status_code == 200


def test_check_that_one_product_and_its_category_are_not_available(flask_app):
    response1 = flask_app.get("/delete/1")
    response2 = flask_app.get("/delete/2")

    assert response1.json["code"] == 404 and response1.json["message"] == "Item not found" and \
           response2.json["code"] == 404 and response2.json["message"] == "Item not found"


def test_check_that_one_product_and_its_category_have_been_removed_from_database(flask_app, empty_db):
    category = Element.query.get(1)
    product = Element.query.get(2)

    assert category is None and product is None
