#!/usr/bin/env python3
"""Host-only Flipper C <-> CURRENT PUBLIC Android Java AI1 contract test.

The Flipper C client and its test fixture come from a temporary private checkout.
The Android protocol/handler come ONLY from the separately checked-out public
Android Satellite repository. No private source or firmware is published.
This cannot prove BLE security, on-device behavior, or language-model inference.
"""
import pathlib
import select
import subprocess
import sys
import tempfile


def line_with_deadline(stream, description):
    readable, _, _ = select.select([stream], [], [], 8)
    if not readable:
        raise TimeoutError(f"Timeout waiting for {description}")
    line = stream.readline()
    if not line:
        raise RuntimeError(f"Unexpected EOF waiting for {description}")
    return line


def run(private_root, public_android_root):
    private_root = pathlib.Path(private_root).resolve(strict=True)
    public_android_root = pathlib.Path(public_android_root).resolve(strict=True)
    if (private_root == public_android_root or
            private_root in public_android_root.parents or
            public_android_root in private_root.parents):
        raise ValueError("The Flipper and Android source roots must be separate")

    c_dir = private_root / "flipper_app" / "satellite_protocol"
    fixture_dir = private_root / "tests" / "integration"
    java_dir = public_android_root / "android_satellite" / "app" / "src" / "main" / "java" / "com" / "flipperai" / "satellite"
    java_names = [
        "SatelliteProtocol", "FrameCodec", "TransportState", "BondGate",
        "PromptLimits", "InferenceRouter", "OfflineDiagnosticEngine",
        "SatelliteRequestHandler", "ProtocolSession"
    ]
    c_sources = [
        fixture_dir / "ai_flipper_client.c",
        c_dir / "ai_wire.c", c_dir / "ai_client.c", c_dir / "ai_link.c"
    ]
    java_sources = [java_dir / (name + ".java") for name in java_names]
    java_sources.append(fixture_dir / "AndroidProtocolServer.java")
    for item in c_sources + java_sources:
        if not item.is_file():
            raise FileNotFoundError(item)

    print("SOURCES: private Momentum C client + public Android Satellite Java", flush=True)
    print("LIMIT: host-side AI1 HELLO/ASK only; not real BLE or AI model inference", flush=True)
    with tempfile.TemporaryDirectory() as tmp:
        c_exec = pathlib.Path(tmp) / "flipper_client"
        subprocess.run([
            "cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
            *map(str, c_sources), "-o", str(c_exec)
        ], check=True, timeout=90)
        subprocess.run([
            "javac", "-encoding", "UTF-8", "-d", tmp,
            *map(str, java_sources)
        ], check=True, timeout=90)

        c = subprocess.Popen([str(c_exec)], stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True, bufsize=1)
        android = subprocess.Popen(["java", "-cp", tmp, "AndroidProtocolServer"],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True, bufsize=1)
        try:
            checks = [
                ("AI1|HELLO|1|flipper-v1\n", "AI1|HELLO_ACK|1|"),
                ("AI1|ASK|2|battery help\n", "AI1|ANSWER|2|"),
            ]
            for expected, prefix in checks:
                request = line_with_deadline(c.stdout, "Flipper C request")
                if request != expected:
                    raise AssertionError(f"Unexpected Flipper request: {request!r}")
                android.stdin.write(request)
                android.stdin.flush()
                reply = line_with_deadline(android.stdout, "public Android Java reply")
                if not reply.startswith(prefix):
                    raise AssertionError(f"Unexpected Android reply: {reply!r}")
                if "ANSWER" in prefix and "Power checks" not in reply:
                    raise AssertionError("Public Android diagnostics did not answer battery query")
                c.stdin.write(reply)
                c.stdin.flush()
            c.stdin.close()
            if c.wait(timeout=8) != 0:
                raise RuntimeError("Flipper C client rejected the Android reply: " + c.stderr.read())
            android.stdin.close()
            if android.wait(timeout=8) != 0:
                raise RuntimeError("Public Android protocol server exited unsuccessfully: " + android.stderr.read())
        finally:
            for proc in (c, android):
                if proc.poll() is None:
                    proc.kill()
                    proc.wait(timeout=5)
                for stream in (proc.stdin, proc.stdout, proc.stderr):
                    if stream is not None:
                        stream.close()
    print("PASS: private Flipper C <-> current PUBLIC Android Java AI1 HELLO/ASK", flush=True)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: run_cross_repository_ai1.py PRIVATE_FLIPPER_ROOT PUBLIC_ANDROID_ROOT")
    run(sys.argv[1], sys.argv[2])
