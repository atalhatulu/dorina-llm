import asyncio, traceback
import viz

async def main():
    try:
        async for ev in viz.generate_stream("Merhaba, 2 arti 3 kac eder?"):
            if ev["type"] == "input":
                print("input ok:", ev["count"])
            else:
                print("token[", ev["step"], "]=", repr(ev["token"]), "L0=", ev["layers"][0])
                if ev["step"] >= 5:
                    print("Ilk 5 token OK, devam ediyor...")
        print("generate_stream TAMAM")
    except Exception:
        traceback.print_exc()

asyncio.run(main())