class Lorag < Formula
  include Language::Python::Virtualenv

  desc "Ask questions over local documents and Apple Notes"
  homepage "https://github.com/imakumar98/homebrew-lorag"
  url "https://github.com/imakumar98/homebrew-lorag/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "06de9d410f579e6ec3600a6a02ff72d11f73a46434dc366a08fd99dc41eab745"
  license :cannot_represent
  head "https://github.com/imakumar98/homebrew-lorag.git", branch: "main"

  depends_on "python@3.14"
  depends_on "ollama"
  depends_on :macos
  depends_on arch: :arm64

  resource "aiohappyeyeballs" do
    url "https://files.pythonhosted.org/packages/71/43/1947f06babed6b3f1d7f38b0c767f52df66bfb2bc10b468c4a7de9eceff2/aiohappyeyeballs-2.7.1-py3-none-any.whl"
    sha256 "9243213661e29250eb41368e5daa826fc017156c3b8a11440826b2e3ed376472"
  end

  resource "aiohttp" do
    url "https://files.pythonhosted.org/packages/85/ed/0357a015892fd68058bf2d39d3fd1958e459b997a7db30aaa6aaa434ae96/aiohttp-3.14.3-cp314-cp314-macosx_11_0_arm64.whl"
    sha256 "db332af25642007330fca8be5c4d194caf2bea7a7fc84415aff3497af5dfee6b"
  end

  resource "aiosignal" do
    url "https://files.pythonhosted.org/packages/fb/76/641ae371508676492379f16e2fa48f4e2c11741bd63c48be4b12a6b09cba/aiosignal-1.4.0-py3-none-any.whl"
    sha256 "053243f8b92b990551949e63930a839ff0cf0b0ebbe0597b0f3fb19e1a0fe82e"
  end

  resource "annotated-doc" do
    url "https://files.pythonhosted.org/packages/3e/30/e900b21425a860e195f32e37657aa1f7c7f2b1bfb26f03ca209b90933c06/annotated_doc-0.0.5-py3-none-any.whl"
    sha256 "117bac03a25ede5df5440e855b32d556049ca169ead221505badf432fed4b101"
  end

  resource "annotated-types" do
    url "https://files.pythonhosted.org/packages/99/91/8acff4f5e50511b911bbccb72b8628a49c68ce14148cd9f6431094859a90/annotated_types-0.8.0-py3-none-any.whl"
    sha256 "f072f4d804ea359e4eaf198b1af7a8b0943881a87f31bb764f8bf219bb9419e0"
  end

  resource "anyio" do
    url "https://files.pythonhosted.org/packages/12/b8/4bd346e22b28902df4d651910f5242c28d84e4a5c2435ca5c3f797ed7e2e/anyio-4.15.1-py3-none-any.whl"
    sha256 "6152fdbbf9a77fdec97731721bebf7c4c44f7c29b424b0065826173efc7ed101"
  end

  resource "attrs" do
    url "https://files.pythonhosted.org/packages/64/b4/17d4b0b2a2dc85a6df63d1157e028ed19f90d4cd97c36717afef2bc2f395/attrs-26.1.0-py3-none-any.whl"
    sha256 "c647aa4a12dfbad9333ca4e71fe62ddc36f4e63b2d260a37a8b83d2f043ac309"
  end

  resource "bcrypt" do
    url "https://files.pythonhosted.org/packages/5d/ba/2af136406e1c3839aea9ecadc2f6be2bcd1eff255bd451dd39bcf302c47a/bcrypt-5.0.0-cp39-abi3-macosx_10_12_universal2.whl"
    sha256 "0c418ca99fd47e9c59a301744d63328f17798b5947b0f791e9af3c1c499c2d0a"
  end

  resource "build" do
    url "https://files.pythonhosted.org/packages/ad/9b/9fb3585dabcd73a1b2a6267f63f62649347c9e6d072c9fde365b105abb2c/build-1.6.1-py3-none-any.whl"
    sha256 "ecd351a4be9d35a9eaaba244a7687143c9c7d4aea6ac964e7e7ddab20cbcf4e7"
  end

  resource "certifi" do
    url "https://files.pythonhosted.org/packages/0b/a7/71ac2cff56fec219ed242bb11b8efb69fcc4bec75db06fb7bfe35de520e6/certifi-2026.7.22-py3-none-any.whl"
    sha256 "62f22742b58a1a33014a2b6b706588a8d7e2a88ae7bd1a6ebe8c992928483775"
  end

  resource "charset-normalizer" do
    url "https://files.pythonhosted.org/packages/e9/40/095ce62fa078483cccc1fa2b36e6bc9580b85422a20ee9f925341c50e44f/charset_normalizer-3.5.1-cp314-cp314-macosx_10_15_universal2.whl"
    sha256 "c428c6c31eb5f4277d7f8eccaf767fbd548ddd5ce3c8b4f4cbbfab3d96b5904c"
  end

  resource "chromadb" do
    url "https://files.pythonhosted.org/packages/34/4c/adcef1f4e82a2ef69ccd3711d55fc289193d54c4c0ff7a0292a3631db46f/chromadb-1.5.9-cp39-abi3-macosx_11_0_arm64.whl"
    sha256 "814b9c95617377f6501e5757d63dfddb554a283a7739c87b9fa573850174e6f3"
  end

  resource "click" do
    url "https://files.pythonhosted.org/packages/58/50/6c0d534c5f134586a8e1ba4e330569e32f057e33372ae556463212fb4cd3/click-8.5.0-py3-none-any.whl"
    sha256 "255bc9599cf7748b4b1a446ccc735421bd08a2ae529a8b88597d3de5664ee360"
  end

  resource "distro" do
    url "https://files.pythonhosted.org/packages/12/b3/231ffd4ab1fc9d679809f356cebee130ac7daa00d6d6f3206dd4fd137e9e/distro-1.9.0-py3-none-any.whl"
    sha256 "7bffd925d65168f85027d8da9af6bddab658135b840670a223589bc0c8ef02b2"
  end

  resource "durationpy" do
    url "https://files.pythonhosted.org/packages/e6/c4/ebdf7837bc4ef6fd98cfb013c28855bb358467bf86c1af011bbc21e21df0/durationpy-0.11-py3-none-any.whl"
    sha256 "a739fe2b8972c250ff72f8e2c488d18cf25f7b852f49ee76048775d5171df30c"
  end

  resource "filelock" do
    url "https://files.pythonhosted.org/packages/cc/06/4f138f618dbea66803291274f228f01daf29f306fe8b96bc30dab765df75/filelock-3.32.6-py3-none-any.whl"
    sha256 "3f16ecd0117feae0dfc147e8c62eb5daeccd8bd800378c3ddf416de9b4feb6b1"
  end

  resource "flatbuffers" do
    url "https://files.pythonhosted.org/packages/e8/2d/d2a548598be01649e2d46231d151a6c56d10b964d94043a335ae56ea2d92/flatbuffers-25.12.19-py2.py3-none-any.whl"
    sha256 "7634f50c427838bb021c2d66a3d1168e9d199b0607e6329399f04846d42e20b4"
  end

  resource "frozenlist" do
    url "https://files.pythonhosted.org/packages/a1/93/72b1736d68f03fda5fdf0f2180fb6caaae3894f1b854d006ac61ecc727ee/frozenlist-1.8.0-cp314-cp314-macosx_11_0_arm64.whl"
    sha256 "4970ece02dbc8c3a92fcc5228e36a3e933a01a999f7094ff7c23fbd2beeaa67c"
  end

  resource "fsspec" do
    url "https://files.pythonhosted.org/packages/fd/3c/6a2bf344106328fd04963664a60b9bb6496fc25df8e962fcdc1367285fb9/fsspec-2026.7.0-py3-none-any.whl"
    sha256 "b57ddbafedfaef7018c1ecab32aa200a9d7ca26b77965f64e48b70061249d279"
  end

  resource "googleapis-common-protos" do
    url "https://files.pythonhosted.org/packages/1a/7a/7d79170c6ce6f12e109df2b3879d6b934010cf4f99aea8de8b7e5408c174/googleapis_common_protos-1.75.3-py3-none-any.whl"
    sha256 "a018d2bf098ca9fb6faa08d5bb780e2a2c2f73c566f069761331386c9596d3f2"
  end

  resource "grpcio" do
    url "https://files.pythonhosted.org/packages/cd/b4/6b76b429f3f9b901cdbc306c81364d708bc957f847a05cbd1046cd2d05d8/grpcio-1.84.0-cp314-cp314-macosx_11_0_universal2.whl"
    sha256 "3de427b05f244ba2c2a9bdc67e7a6731c8340811524ecc4435466549f8af1d17"
  end

  resource "h11" do
    url "https://files.pythonhosted.org/packages/04/4b/29cac41a4d98d144bf5f6d33995617b185d14b22401f75ca86f384e87ff1/h11-0.16.0-py3-none-any.whl"
    sha256 "63cf8bbe7522de3bf65932fda1d9c2772064ffb3dae62d55932da54b31cb6c86"
  end

  resource "hf-xet" do
    url "https://files.pythonhosted.org/packages/4b/69/55b8dcf636142ae660fec1869fcac14c4da2e8412e14d6eee1523be77e9f/hf_xet-1.6.0-cp38-abi3-macosx_11_0_arm64.whl"
    sha256 "f0906082d9932ae0c0057fa194041c22b4e2cdb46b2592ef3b91f020d62a081a"
  end

  resource "httpcore" do
    url "https://files.pythonhosted.org/packages/7e/f5/f66802a942d491edb555dd61e3a9961140fd64c90bce1eafd741609d334d/httpcore-1.0.9-py3-none-any.whl"
    sha256 "2d400746a40668fc9dec9810239072b40b4484b640a8c38fd654a024c7a1bf55"
  end

  resource "httpcore2" do
    url "https://files.pythonhosted.org/packages/7e/0d/117a771a2bb91df334b66bf4da14cd02f21aefbcfe53180f336ce55e8f90/httpcore2-2.13.0-py3-none-any.whl"
    sha256 "35ae5be347aa40467b4a5dc032ac67ebb6d27189fc97e8cebcf99616f6a1bb9e"
  end

  resource "httptools" do
    url "https://files.pythonhosted.org/packages/30/fc/5e7c4cb443370f2090a3aba0453a07384d29ff66b7435bb90e77e1037599/httptools-0.8.0-cp314-cp314-macosx_11_0_arm64.whl"
    sha256 "159e9ab5f701ccd42e555a12f1ad8ff69702910fc1c996cf2bb66e5fcb7a231b"
  end

  resource "httpx" do
    url "https://files.pythonhosted.org/packages/2a/39/e50c7c3a983047577ee07d2a9e53faf5a69493943ec3f6a384bdc792deb2/httpx-0.28.1-py3-none-any.whl"
    sha256 "d909fcccc110f8c7faf814ca82a9a4d816bc5a6dbfea25d6591d6985b8ba59ad"
  end

  resource "httpx2" do
    url "https://files.pythonhosted.org/packages/fe/d1/a0c72b0e006df654709fbc366cc5bcb53e5aee13e1e3395152c6dd293376/httpx2-2.13.0-py3-none-any.whl"
    sha256 "fc12720cedf72faa26cca6b4ca394e05c894e7d7933fc45cafe767960804e49a"
  end

  resource "huggingface_hub" do
    url "https://files.pythonhosted.org/packages/c3/7f/3f886a625043b77312b80da2f2bf00b5ecbf5a73061af1aa0259cd258c9d/huggingface_hub-1.31.0-py3-none-any.whl"
    sha256 "9dbb6a503cbe2494ea666695207e7262d410659e09134059deb83e5480864667"
  end

  resource "idna" do
    url "https://files.pythonhosted.org/packages/57/b0/0e52c878c53f245edd3a11020f20979b3f490f245af532c7cae3027754b5/idna-3.19-py3-none-any.whl"
    sha256 "815e7be7a7806d54abb586dc943addc79e8b2ee16915059658cbeff4b1b43bf4"
  end

  resource "importlib_resources" do
    url "https://files.pythonhosted.org/packages/8a/db/55a262f3606bebcae07cc14095338471ad7c0bbcaa37707e6f0ee49725b7/importlib_resources-7.1.0-py3-none-any.whl"
    sha256 "1bd7b48b4088eddb2cd16382150bb515af0bd2c70128194392725f82ad2c96a1"
  end

  resource "jsonpatch" do
    url "https://files.pythonhosted.org/packages/73/07/02e16ed01e04a374e644b575638ec7987ae846d25ad97bcc9945a3ee4b0e/jsonpatch-1.33-py2.py3-none-any.whl"
    sha256 "0ae28c0cd062bbd8b8ecc26d7d164fbbea9652a1a3693f3b956c1eae5145dade"
  end

  resource "jsonpointer" do
    url "https://files.pythonhosted.org/packages/9e/6a/a83720e953b1682d2d109d3c2dbb0bc9bf28cc1cbc205be4ef4be5da709d/jsonpointer-3.1.1-py3-none-any.whl"
    sha256 "8ff8b95779d071ba472cf5bc913028df06031797532f08a7d5b602d8b2a488ca"
  end

  resource "jsonschema" do
    url "https://files.pythonhosted.org/packages/69/90/f63fb5873511e014207a475e2bb4e8b2e570d655b00ac19a9a0ca0a385ee/jsonschema-4.26.0-py3-none-any.whl"
    sha256 "d489f15263b8d200f8387e64b4c3a75f06629559fb73deb8fdfb525f2dab50ce"
  end

  resource "jsonschema-specifications" do
    url "https://files.pythonhosted.org/packages/41/45/1a4ed80516f02155c51f51e8cedb3c1902296743db0bbc66608a0db2814f/jsonschema_specifications-2025.9.1-py3-none-any.whl"
    sha256 "98802fee3a11ee76ecaca44429fda8a41bff98b00a0f2838151b113f210cc6fe"
  end

  resource "kubernetes" do
    url "https://files.pythonhosted.org/packages/5b/30/a96d47df739689ac0001ade0afefc16e3b477fc2fb426b568515fdc8afce/kubernetes-36.0.3-py2.py3-none-any.whl"
    sha256 "8fde9241c4b298e6374a069dcf728359b4e72c2fb29489a975ba4e1c047cf10f"
  end

  resource "langchain" do
    url "https://files.pythonhosted.org/packages/92/fa/7da07d9977a5e292ef602c1bb911514ff8206e85dc09a66961874345d57a/langchain-1.4.0-py3-none-any.whl"
    sha256 "af1dc0161d30944a52ec7844d9bf890d0497b12ec0703069f3503b4003cbbac3"
  end

  resource "langchain-chroma" do
    url "https://files.pythonhosted.org/packages/ae/35/2a6d1191acaad043647e28313b0ecd161d61f09d8be37d1996a90d752c13/langchain_chroma-1.1.0-py3-none-any.whl"
    sha256 "ff65e4a2ccefb0fb9fde2ff38705022ace402f979d557f018f6e623f7288f0fc"
  end

  resource "langchain-core" do
    url "https://files.pythonhosted.org/packages/e6/18/cf18cfec118b02e003f35300b54d6a1173dc6e4905cffdf5ea49e390a7f9/langchain_core-1.6.3-py3-none-any.whl"
    sha256 "114fe1868c9ed60606662b9dd0074bf3152cc6b0b1522ba37cbd6b04f55ca77d"
  end

  resource "langchain-ollama" do
    url "https://files.pythonhosted.org/packages/2c/b2/c2acb076590a98bee2816ed5f285e00df162a34238f9e276e175e14ebc35/langchain_ollama-1.1.0-py3-none-any.whl"
    sha256 "43ac83a6eacb0f43855810739794dd55019e0d9b17bdcf3ecb3b1991ac3b59dd"
  end

  resource "langchain-protocol" do
    url "https://files.pythonhosted.org/packages/80/c9/f6cbf357d48ccbd18bb394433b1fd7ad9be004eed9377ad08bb85777e5e6/langchain_protocol-0.0.19-py3-none-any.whl"
    sha256 "4cdf879a492a35980fd859ae792d3c65458ccaae504e183c9a10d7eac1f0720f"
  end

  resource "langchain-text-splitters" do
    url "https://files.pythonhosted.org/packages/d3/26/1ef06f56198d631296d646a6223de35bcc6cf9795ceb2442816bc963b84c/langchain_text_splitters-1.1.2-py3-none-any.whl"
    sha256 "a2de0d799ff31886429fd6e2e0032df275b60ec817c19059a7b46181cc1c2f10"
  end

  resource "langgraph" do
    url "https://files.pythonhosted.org/packages/0a/7f/c5c30e4be99ff821029c7ac872a480676bb179c9f3df85ea3f38d13f86d4/langgraph-1.2.11-py3-none-any.whl"
    sha256 "8bab70de7b2d00b5300fb289bcf38d8b241400f3184c1e95e8ce706fb0e8686b"
  end

  resource "langgraph-checkpoint" do
    url "https://files.pythonhosted.org/packages/05/71/3b475f09bd57d3a5649792c66353312b4432afd843f301739dfcebd157f0/langgraph_checkpoint-4.2.0-py3-none-any.whl"
    sha256 "0547fd228935a0b758865de3a3d6d7a2537c308895d0f9ab092ce9151b5da942"
  end

  resource "langgraph-prebuilt" do
    url "https://files.pythonhosted.org/packages/e9/43/3fe1a700b8490ed02679cdbbc8c915eb23a092faf496c9c1118abcd10be3/langgraph_prebuilt-1.1.0-py3-none-any.whl"
    sha256 "51e311747d755b751d5c6b39b0c1446124d3a7643d2515017e6714b323508fc9"
  end

  resource "langgraph-sdk" do
    url "https://files.pythonhosted.org/packages/43/d5/2ad7f3a835c6fcebf58b6669552536ecd52d2dfe4cf49c6c36648fd83572/langgraph_sdk-0.4.4-py3-none-any.whl"
    sha256 "39afe416c91742925e6f8a93715f566d499b36e1b636b804a4ffe3190e4f4e64"
  end

  resource "langsmith" do
    url "https://files.pythonhosted.org/packages/d1/b1/d0c6f84cde25b2443bcdca81f9b30732fc3af602c46f5114fcbe5246b978/langsmith-0.12.4-py3-none-any.whl"
    sha256 "b2edaa49baeec0c7347a84ca0f755039dcff9e9e52f0b9dc26423ec2a98a4dab"
  end

  resource "markdown-it-py" do
    url "https://files.pythonhosted.org/packages/b3/81/4da04ced5a082363ecfa159c010d200ecbd959ae410c10c0264a38cac0f5/markdown_it_py-4.2.0-py3-none-any.whl"
    sha256 "9f7ebbcd14fe59494226453aed97c1070d83f8d24b6fc3a3bcf9a38092641c4a"
  end

  resource "mdurl" do
    url "https://files.pythonhosted.org/packages/b3/38/89ba8ad64ae25be8de66a6d463314cf1eb366222074cfda9ee839c56a4b4/mdurl-0.1.2-py3-none-any.whl"
    sha256 "84008a41e51615a49fc9966191ff91509e3c40b939176e643fd50a5c2196b8f8"
  end

  resource "mmh3" do
    url "https://files.pythonhosted.org/packages/d8/bf/e4be8e728d94387c673510b11120d003f929858169017ab87b852ab5ac6e/mmh3-5.3.0-cp314-cp314-macosx_11_0_arm64.whl"
    sha256 "bc6018e95814fd64ea8357c6e9e5608b97b1f33962c76cff60efd52f76b18a40"
  end

  resource "multidict" do
    url "https://files.pythonhosted.org/packages/f5/b7/f4f4989594f99bc121ad9277090c4e49819b08ab1a96e132b628a9e10b7d/multidict-6.8.0-cp314-cp314-macosx_11_0_arm64.whl"
    sha256 "bea7df027015856ba5d0a88e3b4777ff8cb5c66b58fc108050fe79d4dd9d4d2d"
  end

  resource "numpy" do
    url "https://files.pythonhosted.org/packages/94/75/4640d2d6e4b64a049e48425a82728a41ef4adb61332d2cba68055774878b/numpy-2.5.3-cp314-cp314-macosx_14_0_arm64.whl"
    sha256 "adc1ada2662f8a5f960b8a10d9986897e7499ef07e06d4cfe7197f8cce923c07"
  end

  resource "oauthlib" do
    url "https://files.pythonhosted.org/packages/be/9c/92789c596b8df838baa98fa71844d84283302f7604ed565dafe5a6b5041a/oauthlib-3.3.1-py3-none-any.whl"
    sha256 "88119c938d2b8fb88561af5f6ee0eec8cc8d552b7bb1f712743136eb7523b7a1"
  end

  resource "ollama" do
    url "https://files.pythonhosted.org/packages/c4/ab/d6722beeb2d10f7a3b9ff49375708904fde18f82b5609a0bc4aeb5996a4d/ollama-0.6.2-py3-none-any.whl"
    sha256 "3ad7daab28e5a973445c36a73882a3ef698c2ebb00e21e308652741577509f7d"
  end

  resource "onnxruntime" do
    url "https://files.pythonhosted.org/packages/6a/03/05c9a9234688757d2876ddecf80bba908561ee11debf125bc1a427ae6f48/onnxruntime-1.30.0-cp314-cp314-macosx_14_0_arm64.whl"
    sha256 "8b6169c16a48429890d2f4a0c774ebf54dfe9066a998514aad0518a16d398547"
  end

  resource "opentelemetry-api" do
    url "https://files.pythonhosted.org/packages/ca/6f/a04e900f465ff3221ccc395522503e2d10e79fa21f2723c8e177aae1e0d1/opentelemetry_api-1.44.0-py3-none-any.whl"
    sha256 "94b98c893a91b88657eaac1e3ba89618cdb85be6918196705354f34728b2cdef"
  end

  resource "opentelemetry-exporter-otlp-proto-common" do
    url "https://files.pythonhosted.org/packages/5e/71/65fd9d54c10b860f87c045ccee1264cab7011268895d3528818a29c1172a/opentelemetry_exporter_otlp_proto_common-1.44.0-py3-none-any.whl"
    sha256 "9a9fe61bba73d802904bc989f1d6b4a7b1ee40f06c40e98d6f85af65aaebb694"
  end

  resource "opentelemetry-exporter-otlp-proto-grpc" do
    url "https://files.pythonhosted.org/packages/54/29/6ae42ba32b153ae0a44ae125f0caff2188bbe62d99c82d1768da30864e72/opentelemetry_exporter_otlp_proto_grpc-1.44.0-py3-none-any.whl"
    sha256 "6a1a645ea182a2f59440c51fa8301d309f3324a8f9d65f8395584b064b67ee4e"
  end

  resource "opentelemetry-proto" do
    url "https://files.pythonhosted.org/packages/d1/7c/8be563d68e93bbefa5c8affb82ddcff91b3ad858ce49957ba7b16fd3e0ab/opentelemetry_proto-1.44.0-py3-none-any.whl"
    sha256 "898b155a0e1557afd867478fb6158e8122a46329ca0bb8dc53cc55e98f017f56"
  end

  resource "opentelemetry-sdk" do
    url "https://files.pythonhosted.org/packages/e7/23/ff077e61886ee020a17ce9c8b6fa11c601c8d8345b09ea24f605445df62a/opentelemetry_sdk-1.44.0-py3-none-any.whl"
    sha256 "df081c4c6bcfdb1211e3e86140376792643128a25f8d72d1d27675936e7e96ad"
  end

  resource "opentelemetry-semantic-conventions" do
    url "https://files.pythonhosted.org/packages/a6/0e/49df70d9b81fb5cbae4bbf2a49d865b09bcbcbc4eb53f5851b1027738d78/opentelemetry_semantic_conventions-0.65b0-py3-none-any.whl"
    sha256 "1cacde7b0ad306f84c5ef08c3dbe1bbaf20165bba6f8bff43b670e555a086bcb"
  end

  resource "orjson" do
    url "https://files.pythonhosted.org/packages/8a/0e/b4a4f1e305367245877b967a0bad70fcf001d77c54ac4339a120b66fdae4/orjson-3.12.0-cp314-cp314-macosx_15_0_arm64.whl"
    sha256 "8c3bb86dd10f39b3fbf434b7d5dc7cac77d6fc8ac572ae30a10731ede2c4b647"
  end

  resource "ormsgpack" do
    url "https://files.pythonhosted.org/packages/94/16/24d18851334be09c25e87f74307c84950f18c324a4d3c0b41dabdbf19c29/ormsgpack-1.12.2-cp314-cp314-macosx_10_12_x86_64.macosx_11_0_arm64.macosx_10_12_universal2.whl"
    sha256 "bc68dd5915f4acf66ff2010ee47c8906dc1cf07399b16f4089f8c71733f6e36c"
  end

  resource "overrides" do
    url "https://files.pythonhosted.org/packages/2c/ab/fc8290c6a4c722e5514d80f62b2dc4c4df1a68a41d1364e625c35990fcf3/overrides-7.7.0-py3-none-any.whl"
    sha256 "c7ed9d062f78b8e4c1a7b70bd8796b35ead4d9f510227ef9c5dc7626c60d7e49"
  end

  resource "packaging" do
    url "https://files.pythonhosted.org/packages/63/34/ba1c580383c9eada3711951fef0795c80b829a078d72188184bcab9dd527/packaging-26.3-py3-none-any.whl"
    sha256 "d7193f7c8e4e93f444fde0262bf90af30e16fa0ad0ad44cb553c87339b23cd1c"
  end

  resource "propcache" do
    url "https://files.pythonhosted.org/packages/63/b1/4260d67d6bd85e58a66b72d54ce15d5de789b6f3870cc6bedf8ff9667401/propcache-0.5.2-cp314-cp314-macosx_11_0_arm64.whl"
    sha256 "97797ebb098e670a2f92dd66f32897e30d7615b14e7f59711de23e30a9072539"
  end

  resource "protobuf" do
    url "https://files.pythonhosted.org/packages/f7/6c/3a54a58f2948b0f485df9ecdd06590f15d0a7abf46a89d50c3de709ff4ff/protobuf-7.36.1-cp310-abi3-macosx_10_9_universal2.whl"
    sha256 "3cf2ee25d006cee57294a1196ea43b37feb78e0dcd1e8af5c1aeddb777655aca"
  end

  resource "pybase64" do
    url "https://files.pythonhosted.org/packages/22/39/69828d263af0d31c8ca99d7cae4cf8a5a9f37a1bfc63f2a40afb9cd2a805/pybase64-1.5.0-cp314-cp314-macosx_11_0_arm64.whl"
    sha256 "c3930278a6635dac4dff15f8f336ae643101608160f4525e67a9fc8416061daf"
  end

  resource "pydantic" do
    url "https://files.pythonhosted.org/packages/eb/47/c95ffc2009878c7aac0c5e08528022dcb885933252a88b5f170058014464/pydantic-2.13.5-py3-none-any.whl"
    sha256 "346a034f080da3755d8e9cb5e00e8b07de1d39e4f6e2c87d8ab7cafa0b269a73"
  end

  resource "pydantic-settings" do
    url "https://files.pythonhosted.org/packages/30/a4/2bffa9f8e804325a09867f0e9d30795c80ea9f8d62560bd1b6ad6220eb2f/pydantic_settings-2.15.0-py3-none-any.whl"
    sha256 "0ba092c291c94baceb5eff768aa0d56400a457585bc0175925a5a5510303da42"
  end

  resource "pydantic_core" do
    url "https://files.pythonhosted.org/packages/ae/d5/d8a4eb6d6c7f66b91dd37c576d76e9e60fba900caf5372c17bcf949febc2/pydantic_core-2.46.5-cp314-cp314-macosx_11_0_arm64.whl"
    sha256 "1a353f84de772f423b5ffb11d7ae352fbbef0f446f3c0b0af0f8236d7233606e"
  end

  resource "Pygments" do
    url "https://files.pythonhosted.org/packages/71/46/17f022dd3e953bf20a04a028a21ec746d942f8d2af30fa0f124fa0e6a684/pygments-2.21.0-py3-none-any.whl"
    sha256 "2363c69b61c4a97c838da3b130dcd6468f4848992b21a82f2a63ec34377137d9"
  end

  resource "pypdf" do
    url "https://files.pythonhosted.org/packages/58/13/645df3995075112cb3cce15e8797c205f0f88fb50acc11012b84b071bc22/pypdf-6.18.1-py3-none-any.whl"
    sha256 "ee93a2665670ecf57ee81d197a4ca548f3dc15f9cefc56e59b8140866aaa3de5"
  end

  resource "PyPika" do
    url "https://files.pythonhosted.org/packages/57/83/c77dfeed04022e8930b08eedca2b6e5efed256ab3321396fde90066efb65/pypika-0.51.1-py2.py3-none-any.whl"
    sha256 "77985b4d7ce71b9905255bf12468cf598349e98837c037541cfc240e528aec46"
  end

  resource "pyproject_hooks" do
    url "https://files.pythonhosted.org/packages/bd/24/12818598c362d7f300f18e74db45963dbcb85150324092410c8b49405e42/pyproject_hooks-1.2.0-py3-none-any.whl"
    sha256 "9e5c6bfa8dcc30091c74b0cf803c81fdd29d94f01992a7707bc97babb1141913"
  end

  resource "python-dateutil" do
    url "https://files.pythonhosted.org/packages/ec/57/56b9bcc3c9c6a792fcbaf139543cee77261f3651ca9da0c93f5c1221264b/python_dateutil-2.9.0.post0-py2.py3-none-any.whl"
    sha256 "a8b2bc7bffae282281c8140a97d3aa9c14da0b136dfe83f850eea9a5f7470427"
  end

  resource "python-dotenv" do
    url "https://files.pythonhosted.org/packages/0d/17/c5c6b53ddc18f297992099b3d9ec16c855c0ccc83263a21fe4d1c625ec6c/python_dotenv-1.2.3-py3-none-any.whl"
    sha256 "904552145e8bfed22162c09dab1c2b9b54fefa7b23ba780f4f26ca0316b0f0d9"
  end

  resource "PyYAML" do
    url "https://files.pythonhosted.org/packages/bd/9c/4d95bb87eb2063d20db7b60faa3840c1b18025517ae857371c4dd55a6b3a/pyyaml-6.0.3-cp314-cp314-macosx_11_0_arm64.whl"
    sha256 "34d5fcd24b8445fadc33f9cf348c1047101756fd760b4dacb5c3e99755703310"
  end

  resource "referencing" do
    url "https://files.pythonhosted.org/packages/2c/58/ca301544e1fa93ed4f80d724bf5b194f6e4b945841c5bfd555878eea9fcb/referencing-0.37.0-py3-none-any.whl"
    sha256 "381329a9f99628c9069361716891d34ad94af76e461dcb0335825aecc7692231"
  end

  resource "requests" do
    url "https://files.pythonhosted.org/packages/a0/f4/c67b0b3f1b9245e8d266f0f112c500d50e5b4e83cb6f3b71b6528104182a/requests-2.34.2-py3-none-any.whl"
    sha256 "2a0d60c172f83ac6ab31e4554906c0f3b3588d37b5cb939b1c061f4907e278e0"
  end

  resource "requests-oauthlib" do
    url "https://files.pythonhosted.org/packages/3b/5d/63d4ae3b9daea098d5d6f5da83984853c1bbacd5dc826764b249fe119d24/requests_oauthlib-2.0.0-py2.py3-none-any.whl"
    sha256 "7dd8a5c40426b779b0868c404bdef9768deccf22749cde15852df527e6269b36"
  end

  resource "requests-toolbelt" do
    url "https://files.pythonhosted.org/packages/3f/51/d4db610ef29373b879047326cbf6fa98b6c1969d6f6dc423279de2b1be2c/requests_toolbelt-1.0.0-py2.py3-none-any.whl"
    sha256 "cccfdd665f0a24fcf4726e690f65639d272bb0637b9b92dfd91a5568ccf6bd06"
  end

  resource "rich" do
    url "https://files.pythonhosted.org/packages/82/3b/64d4899d73f91ba49a8c18a8ff3f0ea8f1c1d75481760df8c68ef5235bf5/rich-15.0.0-py3-none-any.whl"
    sha256 "33bd4ef74232fb73fe9279a257718407f169c09b78a87ad3d296f548e27de0bb"
  end

  resource "rpds-py" do
    url "https://files.pythonhosted.org/packages/ba/54/f785cc3d3f60839ca57a5af4927a9f347b07b2799c373fc20f7949f87c7e/rpds_py-2026.6.3-cp314-cp314-macosx_11_0_arm64.whl"
    sha256 "d7469697dce35be237db177d42e2a2ee26e6dcc5fc052078a6fefabd288c6edd"
  end

  resource "shellingham" do
    url "https://files.pythonhosted.org/packages/e0/f9/0595336914c5619e5f28a1fb793285925a8cd4b432c9da0a987836c7f822/shellingham-1.5.4-py2.py3-none-any.whl"
    sha256 "7ecfff8f2fd72616f7481040475a65b2bf8af90a56c89140852d1120324e8686"
  end

  resource "six" do
    url "https://files.pythonhosted.org/packages/b7/ce/149a00dd41f10bc29e5921b496af8b574d8413afcd5e30dfa0ed46c2cc5e/six-1.17.0-py2.py3-none-any.whl"
    sha256 "4721f391ed90541fddacab5acf947aa0d3dc7d27b2e1e8eda2be8970586c3274"
  end

  resource "sniffio" do
    url "https://files.pythonhosted.org/packages/e9/44/75a9c9421471a6c4805dbf2356f7c181a29c1879239abab1ea2cc8f38b40/sniffio-1.3.1-py3-none-any.whl"
    sha256 "2f6da418d1f1e0fddd844478f41680e794e6051915791a034ff65e5f100525a2"
  end

  resource "tenacity" do
    url "https://files.pythonhosted.org/packages/d7/c1/eb8f9debc45d3b7918a32ab756658a0904732f75e555402972246b0b8e71/tenacity-9.1.4-py3-none-any.whl"
    sha256 "6095a360c919085f28c6527de529e76a06ad89b23659fa881ae0649b867a9d55"
  end

  resource "tokenizers" do
    url "https://files.pythonhosted.org/packages/67/49/22da045a91732384d3a3771816bf188dc5a1f702c32e635afa7c679c0bef/tokenizers-0.23.2-cp310-abi3-macosx_11_0_arm64.whl"
    sha256 "986670e43691469dcee610ea0f846f91a8f84e91fc6f7a48d4c064414c0ec2bf"
  end

  resource "tqdm" do
    url "https://files.pythonhosted.org/packages/a7/03/921a3d3c75785aca9ebfbfcabfbc3a1be12e2ab5265deb026d55a5a3f83e/tqdm-4.70.1-py3-none-any.whl"
    sha256 "c293e525e6fef9c20e8728fd4612df02a0aa31bb5fe91ecd93e123b1b7bffa73"
  end

  resource "truststore" do
    url "https://files.pythonhosted.org/packages/19/97/56608b2249fe206a67cd573bc93cd9896e1efb9e98bce9c163bcdc704b88/truststore-0.10.4-py3-none-any.whl"
    sha256 "adaeaecf1cbb5f4de3b1959b42d41f6fab57b2b1666adb59e89cb0b53361d981"
  end

  resource "typer" do
    url "https://files.pythonhosted.org/packages/dc/bf/205d0004930ede8f542fb58f601526fccf4ae7626075ca1e6c4de5d3d652/typer-0.27.2-py3-none-any.whl"
    sha256 "b3a5fc4342d5fc8fda8fc3010b1cf117e9249aab7fae800c2eff62fd3842d97d"
  end

  resource "typing-inspection" do
    url "https://files.pythonhosted.org/packages/67/81/4add07e5172b7ac40d8ed5ff580409a7801a4fe26d529bdd915401dabfbe/typing_inspection-0.4.4-py3-none-any.whl"
    sha256 "65b8397ba37ccbce054456aaccddfc91e6e3083c92824df348d96ca832f3f147"
  end

  resource "typing_extensions" do
    url "https://files.pythonhosted.org/packages/49/d3/b8441a820a491ddfc024b0b0cf0393375b75ea13866d9c66727e54c2fc80/typing_extensions-4.16.0-py3-none-any.whl"
    sha256 "481caa481374e813c1b176ada14e97f1f67a4539ce9cfeb3f350d78d6370c2e8"
  end

  resource "urllib3" do
    url "https://files.pythonhosted.org/packages/7f/3e/5db95bcf282c52709639744ca2a8b149baccf648e39c8cc87553df9eae0c/urllib3-2.7.0-py3-none-any.whl"
    sha256 "9fb4c81ebbb1ce9531cce37674bbc6f1360472bc18ca9a553ede278ef7276897"
  end

  resource "uuid_utils" do
    url "https://files.pythonhosted.org/packages/3a/ea/c735de118ef5c4a6ada1846699e65b3adcac92044e79b83345f90c792fe5/uuid_utils-0.17.1-cp314-cp314-macosx_10_12_x86_64.macosx_11_0_arm64.macosx_10_12_universal2.whl"
    sha256 "f974aa1097b0b8245d8f29550eaac3b431c891ba7c76cc4beaa6ec7bf8cd27b6"
  end

  resource "uvicorn" do
    url "https://files.pythonhosted.org/packages/76/18/0eea75741ee812e9f598b687619ce2454f6c3a1c5cd21ea990ec6bd26f45/uvicorn-0.53.0-py3-none-any.whl"
    sha256 "e8dca71ec86dce5f04e333f0d56cdedf942446e6643b9cea1af0d6d3a02cb03e"
  end

  resource "uvloop" do
    url "https://files.pythonhosted.org/packages/90/cd/b62bdeaa429758aee8de8b00ac0dd26593a9de93d302bff3d21439e9791d/uvloop-0.22.1-cp314-cp314-macosx_10_13_universal2.whl"
    sha256 "3879b88423ec7e97cd4eba2a443aa26ed4e59b45e6b76aabf13fe2f27023a142"
  end

  resource "watchfiles" do
    url "https://files.pythonhosted.org/packages/aa/5d/c9ab3534374a4a67450696905d6ef16a04405448b8dc52bd752ae50423d4/watchfiles-1.2.0-cp314-cp314-macosx_11_0_arm64.whl"
    sha256 "9f04b092229ad2c50126dd3c922c8822e51e605993764a33058d4a791ab42281"
  end

  resource "websocket-client" do
    url "https://files.pythonhosted.org/packages/d5/d2/cc4dc1271e464942db7ee278baae2daa99ee77cb2af744025c04da585a3e/websocket_client-1.9.2-py3-none-any.whl"
    sha256 "e1a673830a9c7bfa47b1cd3d5e4178f4c9651d80a4eab02c9c23a1c3ec6250ce"
  end

  resource "websockets" do
    url "https://files.pythonhosted.org/packages/0f/45/ebec83e6269536aa5932533c67b0af5c781f3e73fdbcd68672dcf43f4f44/websockets-16.1.1-cp314-cp314-macosx_11_0_arm64.whl"
    sha256 "fce6c48559c86d1ac3632ccb1bebc7d5442fbe79bd9bb0e40379ee54be2a4051"
  end

  resource "xxhash" do
    url "https://files.pythonhosted.org/packages/90/9d/f66cf6935f528e575f1ae4d6560d376e7587569747186f4fae8777cadc1b/xxhash-4.0.1-cp314-cp314-macosx_11_0_arm64.whl"
    sha256 "d9f3848ffaf010bdbabdbf4c25641fa258b6227ff27bc74a4d06edef521a4873"
  end

  resource "yarl" do
    url "https://files.pythonhosted.org/packages/18/a9/a07f76f3c44e02b25cc743af5ef93eef27f7013eadca770451b6a6ccb5db/yarl-1.24.5-cp314-cp314-macosx_11_0_arm64.whl"
    sha256 "e42d75862735da90e7fc5a7b23db0c976f737113a54b3c9777a9b665e9cbff75"
  end

  resource "zstandard" do
    url "https://files.pythonhosted.org/packages/8d/09/d0a2a14fc3439c5f874042dca72a79c70a532090b7ba0003be73fee37ae2/zstandard-0.25.0-cp314-cp314-macosx_11_0_arm64.whl"
    sha256 "05df5136bc5a011f33cd25bc9f506e7426c0c9b3f9954f056831ce68f3b6689f"
  end

  def install
    virtualenv_create(libexec, "python3.14")
    venv_python = libexec/"bin/python"
    wheels = buildpath/"_wheels"
    wheels.mkpath
    resources.each do |r|
      dest = wheels/File.basename(r.url)
      cp r.cached_download, dest
      system "python3.14", "-m", "pip", "--python=#{venv_python}",
             "install", "--no-deps", "--ignore-installed", dest
    end
    system "python3.14", "-m", "pip", "--python=#{venv_python}",
           "install", "--no-deps", "--ignore-installed", buildpath
    bin.install_symlink libexec/"bin/lorag"
  end

  def caveats
    <<~EOS
      Start Ollama, pull the default models, then initialize:

        brew services start ollama
        ollama pull llama3.2:3b
        ollama pull nomic-embed-text
        lorag init
    EOS
  end

  test do
    assert_match "usage: lorag", shell_output("#{bin}/lorag -h")
  end
end
