# Chapter 28: CloudFront & CDN

## Overview

Amazon CloudFront is AWS's Content Delivery Network (CDN) — it caches your content at edge locations worldwide to deliver it to users with low latency and high transfer speeds.

## 📖 Understanding CloudFront & CDNs (Intuition First)

Imagine a popular book that everyone in the world wants to read, but there's only one copy in a library in Virginia. Someone in Tokyo has to wait for that book to be shipped across the planet every time they want it — slow and painful. Now imagine you print copies and place them in local libraries in Tokyo, London, Sydney, and hundreds of other cities. Suddenly everyone gets the book from a library near them, instantly. A CDN like CloudFront does exactly this for your website's content: it copies your files to hundreds of "edge locations" around the globe so users get them from a nearby server instead of a distant origin.

The problem CloudFront solves is **latency caused by distance**. Data travels at a finite speed, so a user in Australia hitting a server in Virginia experiences a noticeable delay on every request — and that delay compounds across all the images, scripts, and files a page needs. By serving cached copies from an edge location physically close to the user, CloudFront cuts that round-trip dramatically. Faster pages mean better user experience, higher conversion, and better SEO.

The core mechanism is the **cache**. The first time a user in a region requests a file, CloudFront fetches it from your **origin** (an S3 bucket, a load balancer, or any web server) and stores a copy at the nearby edge location. Every subsequent user in that region gets the cached copy instantly, without touching your origin at all. This does two things at once: it speeds up delivery *and* it dramatically reduces load and bandwidth cost on your origin — the edge absorbs the traffic.

Beyond speed, CloudFront is also a **protection and security layer** sitting in front of your application. Because all traffic flows through CloudFront's globally distributed network, it naturally absorbs traffic spikes and DDoS attacks (integrated with AWS Shield), terminates HTTPS/TLS, and can enforce security rules (via AWS WAF) at the edge before requests ever reach your servers. It's both a performance accelerator and a shield.

The nuance to understand is **what to cache and for how long.** Static content (images, CSS, JS, videos) caches beautifully — it rarely changes. Dynamic, personalized content (a user's account page) shouldn't be cached the same way, or users would see each other's data. Managing cache behavior — TTLs, cache keys, invalidations when content changes — is the art of using a CDN well. "How do CDNs work and when do you use one?" is a common interview question, and the essence is: cache content close to users to reduce latency and origin load.

---

## How CloudFront Works

```
User (Tokyo) ──▶ Nearest Edge Location (Tokyo)
                      │
              Cache HIT? → return cached copy instantly (no origin call)
                      │
              Cache MISS? → fetch from Origin, cache it, return it
                      │
                  Origin (S3 / ALB / web server in us-east-1)

Next Tokyo user → cache HIT → instant, origin untouched
```

## Key Concepts

```
DISTRIBUTION      — a CloudFront configuration (your CDN setup)
ORIGIN            — where the real content lives (S3, ALB, EC2, any HTTP server)
EDGE LOCATION     — a global cache point (hundreds worldwide)
CACHE BEHAVIOR    — rules for how paths are cached (e.g., /images/* vs /api/*)
TTL               — how long content stays cached before re-fetching
INVALIDATION      — force-remove cached content (when you deploy new content)
OAC               — Origin Access Control (lock S3 so only CloudFront can read it)
```

## Setting Up a Distribution (concept + CLI)

```bash
# Create a distribution pointing at an S3 origin (simplified)
aws cloudfront create-distribution \
  --origin-domain-name my-bucket.s3.amazonaws.com \
  --default-root-object index.html

# After deploying new content, invalidate the cache so users get fresh files
aws cloudfront create-invalidation \
  --distribution-id E123ABC \
  --paths "/*"        # or specific paths like "/index.html" (cheaper)
```

## Cache Behaviors (what to cache)

```
Static content (cache aggressively):
  /images/*, /css/*, /js/*, *.mp4  → long TTL (hours/days)

Dynamic/personalized content (don't over-cache):
  /api/*, /account/*  → short/no TTL, or forward cookies/headers

Cache key: what makes a request "the same" for caching purposes.
  Include query strings/headers/cookies in the key only if they change the response.
```

## Security Features at the Edge

```
- HTTPS/TLS termination (free ACM certificates)
- AWS WAF integration — block SQL injection, XSS, bad bots at the edge
- AWS Shield — DDoS protection (Standard is automatic/free)
- Origin Access Control (OAC) — S3 buckets stay private; only CloudFront can read
- Signed URLs / Signed Cookies — restrict access to premium/private content
- Geo-restriction — block or allow specific countries
```

## Edge Compute

```
CloudFront Functions:  lightweight JS at the edge (viewer request/response)
                       - Fast, cheap, for header manipulation, redirects, auth checks
Lambda@Edge:           full Lambda at the edge (more powerful, higher latency)
                       - A/B testing, dynamic content generation, complex logic

Run code close to users without a backend round-trip.
```

## Common Use Cases

```
- Static website hosting (S3 + CloudFront)
- Accelerating a dynamic web app (cache static assets, pass through API)
- Video/media streaming
- Software/file downloads (distribute load globally)
- API acceleration + protection (WAF/Shield in front)
- Serving private content (signed URLs)
```

## CloudFront vs Global Accelerator

```
CloudFront:          caches CONTENT at the edge (HTTP/S, static + dynamic web)
Global Accelerator:  routes TRAFFIC over AWS's backbone to your endpoints
                     (TCP/UDP, non-cacheable, uses static anycast IPs)

Use CloudFront for websites/content; Global Accelerator for
non-HTTP apps needing fast, reliable global routing.
```

---

## 🎯 Interview Quick Points

- CloudFront = AWS's **CDN** — caches content at global **edge locations** near users
- Analogy: local library copies of a popular book instead of shipping from one distant library
- Solves **latency from distance** and **reduces origin load/bandwidth cost**
- Cache **HIT** = served from edge instantly; **MISS** = fetched from origin, then cached
- **Origin** can be S3, ALB, EC2, or any HTTP server
- Cache static content aggressively; be careful with dynamic/personalized content
- **Invalidation** forces fresh content after a deploy (use specific paths to save cost)
- Also a **security layer**: HTTPS/TLS, AWS WAF, Shield (DDoS), geo-restriction, signed URLs
- **OAC** keeps S3 private — only CloudFront can read the bucket
- **CloudFront Functions** (light JS) and **Lambda@Edge** (full compute) run code at the edge
- **CloudFront** caches HTTP content; **Global Accelerator** routes TCP/UDP traffic over AWS backbone
- Cache key design (query strings/headers/cookies) determines what counts as the same request

## Next Steps

Continue to [Secrets Manager & KMS](29-secrets-kms.md).
