
import type { Product } from "@/types/product";
import Image from "next/image";
import { Suspense } from "react";

async function getProducts(): Promise<Product[]> {
  const backendUrl = process.env.BACKEND_URL;

  if (!backendUrl) {
    throw new Error("BACKEND_URL is not configured");
  }

  const response = await fetch(`${backendUrl}/products`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Failed to load products");
  }

  return (await response.json()) as Product[];
}

async function ProductCatalog() {
  const products = await getProducts();

  return (
    <main className="telegram-page mx-auto max-w-3xl">
      <h1 className="mb-8 text-3xl font-bold">
        Каталог
      </h1>

      {products.length === 0 ? (
        <p className="telegram-hint text-center">
          Пока нет товаров
        </p>
      ) : (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
          {products.map((product, index) => (
            <article
              key={product.id}
              className="telegram-product-card overflow-hidden rounded-2xl"
            >
              <div className="relative aspect-square bg-zinc-100">
                <Image
                  src={`/api/images?url=${encodeURIComponent(product.image_url)}`}
                  alt={product.title}
                  fill
                  sizes="(max-width: 640px) 50vw, 33vw"
                  unoptimized
                  loading={index < 2 ? "eager" : "lazy"}
                  className="object-cover"
                />
              </div>

              <div className="p-4">
                <h2 className="text-sm font-semibold">
                  {product.title}
                </h2>
              </div>
            </article>
          ))}
        </div>
      )}
    </main>
  );
}

export default function Home() {
  return (
    <Suspense fallback={<p className="p-6">Загружаем товары...</p>}>
      <ProductCatalog />
    </Suspense>
  );
}