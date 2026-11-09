Workload: routers with 4 (S), 40 (M) or 400 (L) routes (subrouters with own middlewares/404/405 handlers,
router middlewares, NotFound/MethodNotAllowed handlers) and requests aimed at random routes, ~30% 404/405.
The driver calls `router.Match(req, &m)`; check mode also runs the resulting handler to verify the middleware chain.
