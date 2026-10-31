import unittest

from datetime import datetime, timezone
from uuid import uuid4

from app.domain.entities.product import Product, ProductStatus


class TestProduct(unittest.TestCase):

    def create_product(self, title="Test Product"):
        return Product(
            id=uuid4(),
            title=title,
            image_sha256="test_hash",
            request_key="test_request",
            created_at=datetime.now(timezone.utc)
        )

    def test_product_starts_pending(self):
        product = self.create_product()

        self.assertEqual(product.status, ProductStatus.PENDING)
        self.assertIsNone(product.image_key)

    def test_product_can_be_published(self):
        product = self.create_product()

        published = product.mark_ready("products/image.jpg")

        self.assertEqual(published.status, ProductStatus.READY)
        self.assertEqual(published.image_key, "products/image.jpg")
        self.assertEqual(product.status, ProductStatus.PENDING)

    def test_empty_title_is_invalid(self):
        with self.assertRaises(ValueError):
            self.create_product(title="   ")

    def test_cannot_publish_without_image(self):
        product = self.create_product()

        with self.assertRaises(ValueError):
            product.mark_ready("")

    def test_repeated_publish_is_idempotent(self):
        product = self.create_product()
        published = product.mark_ready("products/image.jpg")

        repeated = published.mark_ready("products/image.jpg")

        self.assertIs(repeated, published)

    def test_cannot_replace_published_image(self):
        product = self.create_product()
        published = product.mark_ready("products/image.jpg")

        with self.assertRaises(ValueError):
            published.mark_ready("products/other.jpg")