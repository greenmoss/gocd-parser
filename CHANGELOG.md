# 1.1.2
* Handle stream and parser corner cases
* Switch to dashboard api to retrieve overall status
    * cctray did not include paused pipelines

# 1.1.1
* Switch to Python requests; handles non-api authentication for free!
* Handle corner case of cctray parser

# 1.1.0
* Realize I neglected the change log!
* Add unit tests with vcrpy, enabling major refactoring
* Refactor graph to instead use in-memory graph db: networkx
    * This simplifies and normalizes graph operations; try it!
    * Old method is still available, but subject to deprecation!
* Reduce URL hits on the GoCD server
    * Only look up failing pipelines; we chack this by hitting cctray.xml
* Parse code comparison and materials changes
    * When the value stream is blocked, now you know what caused it

# 1.0.0
* Initial public release
