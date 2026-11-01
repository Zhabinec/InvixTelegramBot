
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
    <main className="mx-auto max-w-3xl px-6 py-10">
      <h1 className="mb-8 text-3xl font-bold">
        Telegram Shop
      </h1>

      {products.length === 0 ? (
        <p>Пока нет товаров</p>
      ) : (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
          {products.map((product) => (
            <article
              key={product.id}
              className="overflow-hidden rounded-2xl border border-zinc-200 bg-white"
            >
              <div className="relative aspect-square bg-zinc-100">
                <Image
                  src={product.image_url}
                  alt={product.title}
                  fill
                  sizes="(max-width: 640px) 50vw, 33vw"
                  unoptimized
                  className="object-cover"
                />
              </div>

              <div className="p-4">
                <h2 className="text-sm font-semibold text-zinc-900">
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