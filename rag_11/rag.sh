#!/bin/bash

# RAG-11 Quick Start Script for Linux/Mac

show_menu() {
    clear
    echo ""
    echo "====== RAG-11 Quick Start Menu ======"
    echo ""
    echo "Commands:"
    echo "  start      - Start the app with Docker Compose"
    echo "  stop       - Stop the app"
    echo "  logs       - View live logs"
    echo "  build      - Rebuild Docker image"
    echo "  shell      - Open bash in container"
    echo "  ingest     - Ingest documents"
    echo "  query      - Ask a question"
    echo "  list       - List ingested documents"
    echo "  help       - Show this menu"
    echo ""
    echo "Usage: ./rag.sh [command]"
    echo "Example: ./rag.sh start"
    echo ""
}

start_app() {
    clear
    echo "Starting RAG-11 with Docker Compose..."
    docker compose up -d
    sleep 2
    docker compose ps
}

stop_app() {
    clear
    echo "Stopping RAG-11..."
    docker compose down
}

show_logs() {
    clear
    echo "Showing live logs (Ctrl+C to exit)..."
    docker compose logs -f
}

build_image() {
    clear
    echo "Building Docker image..."
    docker build -t rag-11:latest .
}

open_shell() {
    clear
    echo "Opening bash in container..."
    docker compose exec rag-app bash
}

ingest_docs() {
    clear
    echo ""
    echo "Ingestion Options:"
    echo "  1. Ingest a single file"
    echo "  2. Ingest a directory"
    echo "  3. Ingest multiple files"
    echo ""
    read -p "Enter choice (1-3): " choice

    case $choice in
        1)
            read -p "Enter file path: " file
            read -p "Enter document title (optional): " title
            docker compose exec rag-app python main.py ingest "$file" --title "$title"
            ;;
        2)
            read -p "Enter directory path: " dir
            docker compose exec rag-app python main.py ingest-dir "$dir" --recursive
            ;;
        3)
            read -p "Enter file paths (space-separated): " files
            docker compose exec rag-app python main.py ingest-many $files
            ;;
        *)
            echo "Invalid choice"
            ;;
    esac
}

query_docs() {
    clear
    read -p "Ask a question: " question
    docker compose exec rag-app python main.py query "$question"
}

list_docs() {
    clear
    docker compose exec rag-app python main.py list
}

show_help() {
    clear
    echo ""
    echo "====== RAG-11 Help ======"
    echo ""
    echo "QUICK START:"
    echo "  ./rag.sh start          Start the app"
    echo "  Open http://localhost:5000 in your browser"
    echo ""
    echo "DOCUMENT MANAGEMENT:"
    echo "  ./rag.sh ingest         Interactive ingest menu"
    echo "  ./rag.sh list           List all documents"
    echo ""
    echo "QUERYING:"
    echo "  ./rag.sh query          Ask a question"
    echo ""
    echo "TROUBLESHOOTING:"
    echo "  ./rag.sh logs           View error logs"
    echo "  ./rag.sh shell          Access container bash"
    echo ""
    echo "For more details, see DEPLOYMENT.md"
    echo ""
}

# Main logic
case "${1:-menu}" in
    start)
        start_app
        ;;
    stop)
        stop_app
        ;;
    logs)
        show_logs
        ;;
    build)
        build_image
        ;;
    shell)
        open_shell
        ;;
    ingest)
        ingest_docs
        ;;
    query)
        query_docs
        ;;
    list)
        list_docs
        ;;
    help)
        show_help
        ;;
    *)
        show_menu
        ;;
esac
