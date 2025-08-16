# Report Analyzer with RAG

**Report Analyzer with RAG**, gelişmiş RAG (Retrieval-Augmented Generation) teknolojisi kullanarak dokümanlardan akıllı soru-cevap sistemi sağlayan kapsamlı bir web uygulamasıdır. [LightRAG](https://github.com/HKUDS/LightRAG) motor altyapısını kullanarak, yüklenen belgelerden bilgi çıkarımı yapabilir ve kullanıcılarla doğal dil ile etkileşim kurabilir.

<div align="center">

![Screenshot 3](https://github.com/user-attachments/assets/a18c4cf7-7c91-473b-9ffe-9b4c291867c3)

![Screenshot 1](https://github.com/user-attachments/assets/49318ded-a610-4bdf-bf0e-a860778f678e)

![Screenshot 2](https://github.com/user-attachments/assets/fe7dbb90-63c1-4672-9fa2-dab30eb5c69a)

</div>

## 🏗️ Sistem Mimarisi

Bu proje **mikroservis** mimarisini benimser ve şu ana bileşenlerden oluşur:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Frontend     │    │     Backend     │    │    LightRAG     │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (RAG Motor)   │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 9621    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                 │                         │
                                 │                         │
                        ┌─────────▼──┐          ┌──────────┼─────────┐─────────┐
                        │PostgreSQL  │          │          │         │         │
                        │(Backend)   │          │          │         │         │
                        │Port: 5433  │    ┌─────▼────┐  ┌──▼───┐  ┌──▼───┐  ┌──▼─────┐
                        └────────────┘    │PostgreSQL│  │Redis │  │Qdrant│  │ Neo4j  │
                                          │(LightRAG)│  │6379  │  │6333  │  │ 7474   │
                                          │Port: 5432│  └──────┘  └──────┘  └────────┘
                                          └──────────┘
```

### Bileşenler

- **Frontend**: React/Next.js tabanlı modern web arayüzü
- **Backend**: FastAPI tabanlı API servisi, sohbet geçmişi yönetimi
- **LightRAG**: Ana RAG motor, doküman işleme ve AI sorgu motoru ([GitHub](https://github.com/HKUDS/LightRAG))
- **PostgreSQL (Backend)**: Backend'e özel veritabanı (sohbet geçmişi, kullanıcı verileri) - Port 5433
- **PostgreSQL (LightRAG)**: LightRAG'a özel veritabanı (isteğe bağlı storage) - Port 5432
- **Redis**: LightRAG için anahtar-değer depolaması ve önbellek
- **Qdrant**: LightRAG için vektör veritabanı (doküman embedding'leri)
- **Neo4j**: LightRAG için graf veritabanı (bilgi grafiği ve ilişkiler)

## 🚀 Hızlı Başlangıç

### Gereksinimler

- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Git**
- En az **8GB RAM** (tüm servisler için)
- **10GB** boş disk alanı

### 1. Projeyi İndirin

```bash
git clone <repository-url>
cd report-analyzer-with-rag
```

### 2. Ortam Değişkenlerini Ayarlayın

#### LightRAG Konfigürasyonu

```bash
# LightRAG konfigürasyon dosyalarını oluşturun
cp LightRAG/env.example LightRAG/.env
cp LightRAG/config.ini.example LightRAG/config.ini
```

**LightRAG/.env** dosyasını düzenleyin:

```env
# LLM Yapılandırması (OpenAI)
LLM_BINDING=openai
LLM_MODEL=gpt-4o-mini
LLM_BINDING_HOST=https://api.openai.com/v1
LLM_BINDING_API_KEY=your_openai_api_key_here

# Embedding Yapılandırması (OpenAI)
EMBEDDING_BINDING=openai
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIM=1536
EMBEDDING_BINDING_HOST=https://api.openai.com/v1
EMBEDDING_BINDING_API_KEY=your_openai_api_key_here

# LightRAG Veritabanı Bağlantıları (Docker servisleri için)
# PostgreSQL - İsteğe bağlı storage (alternatif olarak)
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=lightrag
POSTGRES_PASSWORD=lightrag123
POSTGRES_DATABASE=lightragdb

# Redis - Anahtar-değer depolaması
REDIS_URI=redis://redis:6379

# Qdrant - Vektör veritabanı
QDRANT_URL=http://qdrant:6333

# Neo4j - Graf veritabanı
NEO4J_URI=bolt://neo4j:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=lightrag123

# Storage Konfigürasyonu (Production için önerilen)
LIGHTRAG_KV_STORAGE=RedisKVStorage
LIGHTRAG_DOC_STATUS_STORAGE=PGDocStatusStorage
LIGHTRAG_GRAPH_STORAGE=Neo4JStorage
LIGHTRAG_VECTOR_STORAGE=QdrantVectorDBStorage

# Alternatif: PostgreSQL kullanmak isterseniz
# LIGHTRAG_KV_STORAGE=PGKVStorage
# LIGHTRAG_DOC_STATUS_STORAGE=PGDocStatusStorage
# LIGHTRAG_GRAPH_STORAGE=PGGraphStorage
# LIGHTRAG_VECTOR_STORAGE=PGVectorStorage

# Sunucu Yapılandırması
HOST=0.0.0.0
PORT=9621
SUMMARY_LANGUAGE=Turkish
```

**LightRAG/config.ini** dosyasını düzenleyin:

```ini
[neo4j]
uri = bolt://neo4j:7687
username = neo4j
password = lightrag123

[mongodb]
uri = mongodb+srv://name:password@your-cluster-address
database = lightrag

[redis]
uri = redis://redis:6379/1

[qdrant]
uri = http://qdrant:6333

[postgres]
host = postgres
port = 5432
user = lightrag
password = lightrag123
database = lightragdb
workspace = default
max_connections = 12

[memgraph]
uri = bolt://localhost:7687
```

#### Backend Konfigürasyonu

**backend/.env** dosyası oluşturun:

```env
# Veritabanı Yapılandırması
DATABASE_URL=postgresql://backend:backend123@postgres_backend:5432/backend_db

# LightRAG Server Yapılandırması
LIGHTRAG_SERVER_URL=http://lightrag:9621
LIGHTRAG_API_KEY=your-secure-api-key-here

# Uygulama Yapılandırması
APP_NAME=Report Analyzer with RAG Backend
DEBUG=false
CORS_ORIGINS=["http://localhost:3000", "http://frontend:3000"]

# Dosya Depolama Yapılandırması
UPLOAD_DIR=./uploads
DOCUMENTS_DIR=./static/documents
MAX_FILE_SIZE=52428800

# Güvenlik Yapılandırması
SECRET_KEY=your-super-secret-key-change-in-production-must-be-32-chars
```

#### Frontend Konfigürasyonu

**frontend/.env.local** dosyası oluşturun:

```env
# Backend API URL'i
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```


### 3. Sistemi Başlatın

**Önemli**: Yukarıdaki adımda oluşturulan tüm .env dosyalarının doğru yerleştirildiğinden emin olun:
- `LightRAG/.env`
- `LightRAG/config.ini`
- `backend/.env`
- `frontend/.env.local`

```bash
# Environment dosyalarının varlığını kontrol edin
ls -la LightRAG/.env LightRAG/config.ini backend/.env frontend/.env.local

# Tüm servisleri başlat
docker-compose up -d

# İlk başlatma loglarını izleyin
docker-compose logs -f
```

### 4. Servislerin Durumunu Kontrol Edin

```bash
# Çalışan konteynerleri görmek için
docker-compose ps

# Sağlık kontrolü
curl http://localhost:8000/health
curl http://localhost:9621/health
```

### 5. Uygulamaya Erişin

- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs
- **LightRAG WebUI**: http://localhost:9621
- **Neo4j Browser**: http://localhost:7474 (kullanıcı: neo4j, şifre: lightrag123)

## 🔧 Detaylı Konfigürasyon

### Embedding Modeli Kurulumu

Bu konfigürasyonda LightRAG, hem LLM hem de embedding'ler için OpenAI API kullanıyor. Bu nedenle ayrı bir embedding servisi kurmanıza gerek yok.

**Alternatif olarak Ollama kullanmak isterseniz:**

```bash
# Ollama kurulumu (Linux/macOS)
curl -fsSL https://ollama.ai/install.sh | sh

# Embedding modelini indirin
ollama pull bge-m3:latest

# Ollama servisini başlatın
ollama serve
```

**Windows için**: [Ollama Windows kurulum sayfasını](https://ollama.ai/download/windows) ziyaret edin.

**Ollama kullanmak için .env dosyasını şu şekilde değiştirin:**

```env
EMBEDDING_BINDING=ollama
EMBEDDING_MODEL=bge-m3:latest
EMBEDDING_DIM=1024
EMBEDDING_BINDING_HOST=http://host.docker.internal:11434
# EMBEDDING_BINDING_API_KEY satırını kaldırın veya # ile yorumlayın
```

### OpenAI API Anahtarı

1. [OpenAI Platform](https://platform.openai.com/api-keys) sayfasına gidin
2. Yeni bir API anahtarı oluşturun
3. `LightRAG/.env` dosyasındaki hem `LLM_BINDING_API_KEY` hem de `EMBEDDING_BINDING_API_KEY` değerlerini güncelleyin

**Not**: Aynı API anahtarını her iki yerde de kullanabilirsiniz.

### Alternatif LLM Yapılandırması

OpenAI yerine Ollama kullanmak isterseniz:

```env
# LightRAG/.env dosyasında
LLM_BINDING=ollama
LLM_MODEL=llama3.1:8b
LLM_BINDING_HOST=http://host.docker.internal:11434
```

## 📝 Kullanım

### Doküman Yükleme

1. Frontend'e gidin: http://localhost:3000
2. Sol menüden "Dokümanlar" seçin
3. PDF dosyalarını sürükleyip bırakın
4. Dosyalar otomatik olarak işlenecek ve bilgi grafiğine eklenecek

### Sohbet

1. Ana sayfada sohbet arayüzünü kullanın
2. Yüklediğiniz dokümanlar hakkında sorular sorun
3. Sistem, ilgili bilgileri bulup kapsamlı yanıtlar verecek

### Graf Görselleştirme

1. LightRAG WebUI'ye gidin: http://localhost:9621
2. "Graph" sekmesinde bilgi grafiğini görün
3. Dokümanlardan çıkarılan varlıklar ve ilişkileri keşfedin





## 🛠️ Geliştirme

### Geliştirme Modu

```bash
# Backend'i geliştirme modunda çalıştırın
cd backend
pip install -r requirements.txt
python main.py

# Frontend'i geliştirme modunda çalıştırın
cd frontend
npm install
npm run dev
```

### API Dokümantasyonu

- **Backend Swagger UI**: http://localhost:8000/docs
- **Backend ReDoc**: http://localhost:8000/redoc

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some amazing feature'`)
4. Branch'i push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 🔗 Referanslar

### LightRAG

Bu proje [LightRAG](https://github.com/HKUDS/LightRAG) "Simple and Fast Retrieval-Augmented Generation" sistemini kullanır.

**Akademik Atıf:**
```
@article{guo2024lightrag,
  title={LightRAG: Simple and Fast Retrieval-Augmented Generation},
  author={Zirui Guo and Lianghao Xia and Yanhua Yu and Tu Ao and Chao Huang},
  year={2024},
  eprint={2410.05779},
  archivePrefix={arXiv},
  primaryClass={cs.IR}
}
```

- **ArXiv Paper**: https://arxiv.org/abs/2410.05779
- **GitHub Repository**: https://github.com/HKUDS/LightRAG
- **License**: MIT License
- **Stars**: 18.8k+ ⭐

---

**Not**: İlk çalıştırmada sistem kaynaklarının indirilmesi nedeniyle başlatma süreci uzun olabilir. Sabırlı olun ve logları takip edin. 