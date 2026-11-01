
import { NextRequest } from "next/server";

const MINIO_ORIGIN = "http://127.0.0.1:9000";

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

    const upstreamUrl = new URL(
      `${url.pathname}${url.search}`,
      upstreamOrigin,
    );

    const response = await fetch(upstreamUrl, {
      headers: {
        Host: url.host,
      },
      cache: "no-store",
      redirect: "error",
    });
    if (!response.ok || !response.body) {
      return new Response("Image unavailable", { status: 502 });
    }

    const contentType = response.headers.get("content-type");

    if (!contentType?.startsWith("image/")) {
      return new Response("Invalid image content", { status: 502 });
    }

    return new Response(response.body, {
      headers: {
        "Content-Type": contentType,
        "Cache-Control": "private, no-store",
        "X-Content-Type-Options": "nosniff",
      },
    });
  } catch {
    return new Response("Failed to load image", { status: 502 });
  }
}
