# KyotoMMR

Kyoto University Multi-Modal Recording system

このソフトウェアは複数の音声と動画を並列で記録するためのものです。
- SensorController ... 複数のセンサの記録開始・終了を操作するサーバ
- AudioCapture ... pyaudioを用いて音声を記録するクライアント
- VideoCapture ... opencv-pythonを用いて動画を記録するクライアント
- ExeLauncher ... 指定された任意のコマンドを実行するクライアント