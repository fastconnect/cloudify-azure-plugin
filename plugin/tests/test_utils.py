﻿from cloudify.state import current_ctx
from cloudify.mocks import MockCloudifyContext


AZURE_USERNAME = 'api@victoroudinfastconnect.onmicrosoft.com'
SUBSCRIPTION_ID = '18d68acb-caef-42cb-9dde-050ed320998c'
AZURE_PASSWORD = '123@c!0udify'
COMPUTE_USER = 'administrateur'
COMPUTE_PASSWORD = 'Cloud?db'
PUBLIC_KEY = """---- BEGIN SSH2 PUBLIC KEY ----
Comment: "rsa-key-20150826"
AAAAB3NzaC1yc2EAAAABJQAAAQEAwZ2iu7gZGe/Y92+6Y8wobBmBLQUuQudR1iIG
F0jR5oxkph3YAQ8h07B6m0UXVa21Mfkk45K9I0MfabxdTCEBYQQmUU+AEA11AGVf
q/vVdd6dO5ZsTWnqt/VU62vjCCG3DhruKVyjz2fSUsKhSjVp2p0Ac7ME5fsxtUv6
CEjPsRgjOQHb8IM3gLA3YIYcufkPBXgV4aFKceP11mXiEmK1g07HDI+LGo0pT3xO
AlXSDkwcfTVWsdDGnzVILJUs/iHRlQvEZHNDS1JNWKQtJFEYMYY/7kglojXnSMwN
n9zr6OoedfNrMjHax5Ne1j9+iVGAul1Hap+glTqv01o1YtV8Lw==
---- END SSH2 PUBLIC KEY ----"""
PRIVATE_KEY = """PuTTY-User-Key-File-2: ssh-rsa
Encryption: none
Comment: rsa-key-20150826
Public-Lines: 6
AAAAB3NzaC1yc2EAAAABJQAAAQEAwZ2iu7gZGe/Y92+6Y8wobBmBLQUuQudR1iIG
F0jR5oxkph3YAQ8h07B6m0UXVa21Mfkk45K9I0MfabxdTCEBYQQmUU+AEA11AGVf
q/vVdd6dO5ZsTWnqt/VU62vjCCG3DhruKVyjz2fSUsKhSjVp2p0Ac7ME5fsxtUv6
CEjPsRgjOQHb8IM3gLA3YIYcufkPBXgV4aFKceP11mXiEmK1g07HDI+LGo0pT3xO
AlXSDkwcfTVWsdDGnzVILJUs/iHRlQvEZHNDS1JNWKQtJFEYMYY/7kglojXnSMwN
n9zr6OoedfNrMjHax5Ne1j9+iVGAul1Hap+glTqv01o1YtV8Lw==
Private-Lines: 14
AAABAD7LV195+k2Z5YCunVDMl30BWlPKVDFfx4O4Afm2wJ3MqwVxdnziUCj691Tz
0Dd2m6GBPGV7svat/Fmk3/0DyRiLuWZ6phMLSIqBvinwz5vZfxo+n6pnimUs+PJo
LfTMqhJpmVmF1ENERDaET/xkWa6vdcSow1GB5pup8DoJxtGmZj7ieR8gFftxeK4Y
JGQR5G6HIIE8Oyl8JChSkRRx7vGAXH6EbkB6UUvZASlg1MqUkHu35q6zuv1XT1hp
LW96j3C52gd+/xY+a6mLMGGLHnIGXkImhGjnpqrlTnmWe50O8OLXW6xijAioNf6U
CvHAo0nRrBUMneWZa64Rq0+I8s0AAACBAOFPWm8YL7zjvJGxa3fnfmfRL2Ai8xXs
fnp4xZtZAHxYtXa9ydTvzx20EJtAB+bcZ+dWc14StmYcTC4bNQAGcycwtutyfgcO
jQK/0axUvDKNBrh4G3oAZ0XlL1hJX3k4W/XSc1HmJ+Hbyk1zsYzO7nFIhsEAnrPQ
JYGA62oN6/wNAAAAgQDb/RfMuFs21ascQPrfSJjRiigRhYnTcCa2i/cHZQLtwfgz
HgK3jpo7nDlEgriwa+93qUrxWcWKoHE6wMaLip9wHhfOBYL/DYTT+LqrotKdGkE6
KjXos68KKgRYtO11jErB6BK+oy9z0RfAPEV6plEX+OVefm9bQSbM+bhQdQM+KwAA
AIABfPypznjcBgmEpwEaCOSlrvpPYKlw4DEecyFYluACG9OR79LBPFyBl6GuP7qH
niyuCcdMJ9owk3c4O3/C5YWQmapwkymUnGoABmVqfehdeJ96dIuNYLl3pvUYGYzF
4gTqTpTEmSxShVTV5JVkWV8HK2Yrmu5CKMTCNzOmn67wmw==
Private-MAC: 53f9634ff34570f0b455ab5543f2cdb30a3f5769"""