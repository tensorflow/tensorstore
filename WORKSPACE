workspace(name = "store_tensor_www")

http_archive(
    name = "io_bazel_rules_closure",
    sha256 = "7fb23196455e26d83559cf8a2afa13f720d512f10215228186badfe6d6ad1b18",
    strip_prefix = "rules_closure-0.6.0",
    urls = [
        "https://mirror.bazel.build/github.com/bazelbuild/rules_closure/archive/0.6.0.tar.gz",
        "https://github.com/bazelbuild/rules_closure/archive/0.6.0.tar.gz",
    ],
)

load("@io_bazel_rules_closure//closure:defs.bzl", "closure_repositories")

closure_repositories()
