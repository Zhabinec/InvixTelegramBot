
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock

from app.application.ports.product_repository import ProductRepository
from app.application.ports.image_storage import ImageStorage
from app.application.use_cases.create_product import (
    CreateProductCommand,
    CreateProductUseCase,
)
from app.domain.entities.product import ProductStatus
from app.domain.value_objects.image_key import ImageKey
from app.domain.value_objects.request_key import RequestKey


class TestCreateProductUseCase(IsolatedAsyncioTestCase):

    async def test_creates_product(self):
        repository = AsyncMock(spec=ProductRepository)
        storage = AsyncMock(spec=ImageStorage)

        repository.reserve.side_effect = lambda product: product

        async def mark_ready(product_id, image_key):
            product = repository.reserve.await_args.args[0]
            self.assertEqual(product.id, product_id)
            return product.mark_ready(image_key)

        repository.mark_ready.side_effect = mark_ready

        command = CreateProductCommand(
            title="Кроссовки",
            image_bytes=b"\xff\xd8\xff" + b"test-image",
            content_type="image/jpeg",
            request_key=RequestKey("tg:123:456")
        )

        use_case = CreateProductUseCase(repository, storage)
        product = await use_case.execute(command)

        self.assertEqual(product.status, ProductStatus.READY)
        self.assertEqual(product.title, "Кроссовки")
        self.assertIsInstance(product.image_key, ImageKey)

        repository.reserve.assert_awaited_once()
        storage.upload.assert_awaited_once_with(
            key=product.image_key,
            content=command.image_bytes,
            content_type=command.content_type
        )
        repository.mark_ready.assert_awaited_once_with(
            product_id=product.id,
            image_key=product.image_key
        )


    async def test_repeated_request_does_not_upload_twice(self):
        repository = AsyncMock(spec=ProductRepository)
        storage = AsyncMock(spec=ImageStorage)

        saved_product = None

        def reserve(candidate):
            nonlocal saved_product

            if saved_product is None:
                saved_product = candidate

            return saved_product

        def mark_ready(product_id, image_key):
            nonlocal saved_product

            self.assertEqual(saved_product.id, product_id)
            saved_product = saved_product.mark_ready(image_key)

            return saved_product

        repository.reserve.side_effect = reserve
        repository.mark_ready.side_effect = mark_ready

        command = CreateProductCommand(
            title="Кроссовки",
            image_bytes=b"\xff\xd8\xff" + b"test-image",
            content_type="image/jpeg",
            request_key=RequestKey("tg:123:456")
        )

        use_case = CreateProductUseCase(repository, storage)

        first = await use_case.execute(command)
        second = await use_case.execute(command)

        self.assertIs(first, second)
        self.assertEqual(first.status, ProductStatus.READY)

        self.assertEqual(repository.reserve.await_count, 2)
        storage.upload.assert_awaited_once()
        repository.mark_ready.assert_awaited_once()
