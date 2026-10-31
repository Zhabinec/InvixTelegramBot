
import unittest
from uuid import uuid4

from app.domain.value_objects.image_key import ImageKey


class TestImageKey(unittest.TestCase):

    def test_valid_key(self):
        product_id = uuid4()

        key = ImageKey.for_product(product_id)

        self.assertEqual(
            key.value,
            f"products/{product_id}.jpg"
        )

    def test_invalid_prefix(self):
        with self.assertRaises(ValueError):
            ImageKey(f"images/{uuid4()}.jpg")

    def test_invalid_uuid(self):
        with self.assertRaises(ValueError):
            ImageKey("products/hello.jpg")

    def test_invalid_extension(self):
        with self.assertRaises(ValueError):
            ImageKey(f"products/{uuid4()}.png")
