
import { request as httpRequest } from "node:http";
import { Readable } from "node:stream";
import { NextRequest } from "next/server";

const MINIO_ORIGIN = "http://127.0.0.1:9000";

function fetchImage(
  url: URL,
  upstreamOrigin: string,
): Promise<Response> {
  const upstream = new URL(upstreamOrigin);

  return new Promise((resolve, reject) => {
    const request = httpRequest(
      {
        hostname: upstream.hostname,
        port: upstream.port,
        method: "GET",
        path: `${url.pathname}${url.search}`,
        headers: {
          Host: url.host,
        },
      },
      (response) => {
        const contentType = response.headers["content-type"];

        if (
          response.statusCode !== 200 ||
          typeof contentType !== "string" ||
          !contentType.startsWith("image/")
        ) {
          response.resume();
          resolve(
            new Response("Image unavailable", { status: 502 }),
          );
          return;
        }

        resolve(
          new Response(
            Readable.toWeb(response) as ReadableStream<Uint8Array>,
            {
              headers: {
                "Content-Type": contentType,
                "Cache-Control": "private, no-store",
                "X-Content-Type-Options": "nosniff",
              },
            },
          ),
        );
      },
    );

    request.setTimeout(10000, () => {
      request.destroy(new Error("MinIO request timed out"));
    });

    request.on("error", reject);
    request.end();
  });
}

export async function GET(request: NextRequest) {
  const imageUrl = request.nextUrl.searchParams.get("url");

  if (!imageUrl) {
    return new Response("Image URL is required", { status: 400 });
  }

  let url: URL;

  try {
    url = new URL(imageUrl);
  } catch {
    return new Response("Invalid image URL", { status: 400 });
  }

  if (
    url.origin !== MINIO_ORIGIN ||
    !url.pathname.startsWith("/products/") ||
    url.username ||
    url.password
  ) {
    return new Response("Image URL is not allowed", { status: 403 });
  }

  try {
    const upstreamOrigin =
      process.env.MINIO_UPSTREAM_ORIGIN ?? MINIO_ORIGIN;

    return await fetchImage(url, upstreamOrigin);
  } catch {
    return new Response("Failed to load image", { status: 502 });
  }
}
