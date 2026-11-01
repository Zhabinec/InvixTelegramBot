
import type { Product } from "@/types/product";

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

export default async function Home() {
  const products = await getProducts();

  return (
    <main className="mx-auto max-w-3xl px-6 py-10">
      <h1 className="mb-8 text-3xl font-bold">
        Telegram Shop
      </h1>

      {products.length === 0 ? (
        <p>Пока нет товаров</p>
      ) : (
        <div className="space-y-4">
          {products.map((product) => (
            <article
              key={product.id}
              className="rounded-xl border p-5"
            >
              <h2 className="text-xl font-semibold">
                {product.title}
              </h2>

              <a
                href={product.image_url}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-3 inline-block text-blue-500 underline"
              >
                Открыть фотографию
              </a>
            </article>
          ))}
        </div>
      )}
    </main>
  );
}
