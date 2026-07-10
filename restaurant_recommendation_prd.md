# 🍽️ Restaurant Recommendation System — Project PRD & Technical Blueprint

> **Status:** Completed
> **Team:** College Project
> **Last Updated:** July 2026

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Goals & Scope](#2-goals--scope)
3. [System Architecture](#3-system-architecture)
4. [Data Structures Used](#4-data-structures-used)
5. [Algorithms Used](#5-algorithms-used)
6. [Complete System Flow](#6-complete-system-flow)
7. [Module Breakdown](#7-module-breakdown)
8. [Tech Stack](#8-tech-stack)
9. [Folder Structure](#9-folder-structure)
10. [Mock Data Plan](#10-mock-data-plan)
11. [Build Phases & Tasks](#11-build-phases--tasks)
12. [AI Prompts to Build Each Module](#12-ai-prompts-to-build-each-module)

---

## 1. Project Overview

A **Restaurant Recommendation System** that takes user preferences (cuisine, budget, location) and returns a ranked list of restaurants using classical DSA algorithms. The system demonstrates practical use of graphs, tries, heaps, hash maps, and sorting in a real-world problem.

This is built as a **Python-based CLI + optional web UI** project for college submission, with clean separation of modules so team members can work in parallel.

---

## 2. Goals & Scope

### What we are building
- Search restaurants by name or cuisine (with autocomplete)
- Recommend restaurants based on user taste profile
- Rank results using a scoring engine
- Filter by budget and location

### What we are NOT building (out of scope)
- Real-time data from Zomato/Swiggy APIs
- User login/authentication
- Payment or ordering functionality
- Mobile app

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        USER INPUT                        │
│         (cuisine, budget, location, preferences)         │
└────────────────────────┬────────────────────────────────┘
                         │
              ┌──────────▼──────────┐
              │    Search Module     │
              │    (Trie — O(m))     │
              └──────────┬──────────┘
                         │
              ┌──────────▼──────────┐
              │   Profile Lookup     │
              │  (HashMap — O(1))    │
              └──────────┬──────────┘
                         │
              ┌──────────▼──────────┐
              │  Similarity Engine   │
              │ (Graph + Dijkstra +  │
              │  Cosine Similarity)  │
              └──────────┬──────────┘
                         │
              ┌──────────▼──────────┐
              │   Ranking Engine     │
              │ (Max-Heap — O(log n))│
              └──────────┬──────────┘
                         │
              ┌──────────▼──────────┐
              │   Filtered Output    │
              │  (Merge Sort + DSA)  │
              └──────────┬──────────┘
                         │
              ┌──────────▼──────────┐
              │  Top-K Results UI    │
              │  (CLI or Web)        │
              └─────────────────────┘
```

---

## 4. Data Structures Used

### 4.1 Graph
- **What:** Nodes = Restaurants, Users, Cuisines. Edges = ratings, shared tags, similarity.
- **Why:** Restaurants and user preferences are naturally interconnected. A graph lets us traverse these connections.
- **Operations:** Add node, add edge, BFS/DFS traversal, weighted shortest path.

### 4.2 Trie (Prefix Tree)
- **What:** A tree where each node is a character; paths from root spell out words.
- **Why:** Enables O(m) autocomplete for restaurant names and cuisines (m = length of query).
- **Operations:** Insert word, search prefix, return all matches.

### 4.3 Max-Heap (Priority Queue)
- **What:** A binary tree where the parent always has a higher value than children.
- **Why:** Efficient Top-K extraction — we don't need to sort all results, just get the best N.
- **Operations:** Insert O(log n), extract max O(log n), peek O(1).

### 4.4 Hash Map (Dictionary)
- **What:** Key-value store with O(1) average lookup.
- **Why:** Store user profiles, restaurant metadata, cache similarity scores.
- **Operations:** Get, set, delete — all O(1) average.

---

## 5. Algorithms Used

### 5.1 Dijkstra's Algorithm
- **Used for:** Traversing the restaurant similarity graph to find the "closest" restaurants to a user's taste.
- **How:** Edge weights = inverse similarity score. Lower weight = more similar.
- **Complexity:** O((V + E) log V) with a min-heap.

### 5.2 BFS (Breadth-First Search)
- **Used for:** Exploring restaurants connected by shared cuisine tags or user overlap.
- **How:** Start from a "seed" restaurant and expand level by level — each level is a degree further in taste.
- **Complexity:** O(V + E).

### 5.3 Cosine Similarity
- **Used for:** Scoring how similar a restaurant's feature vector is to the user's preference vector.
- **How:** Each restaurant is represented as a vector (e.g., [spicy=0.8, veg=1, price=2, rating=4.2]). The angle between the user vector and restaurant vector gives the similarity score.
- **Formula:** `similarity = (A · B) / (||A|| × ||B||)`

### 5.4 Merge Sort
- **Used for:** Final sorting of candidate restaurants by composite score before displaying.
- **Complexity:** O(n log n), stable sort.

---

## 6. Complete System Flow

```
Step 1 — User enters query
         e.g., "Italian restaurants under ₹500"

Step 2 — Trie Search
         → Autocomplete suggestions as user types
         → Returns list of matching restaurant IDs

Step 3 — HashMap Lookup
         → Fetch full restaurant data for each ID
         → Fetch user's preference profile (past ratings, liked cuisines)

Step 4 — Graph Traversal (BFS from matched nodes)
         → Find restaurants connected to matched ones via shared tags
         → Expand candidate pool

Step 5 — Dijkstra on Similarity Graph
         → Find shortest path from user's taste node to restaurant nodes
         → Shorter path = more relevant recommendation

Step 6 — Cosine Similarity Scoring
         → Score each candidate restaurant against user preference vector
         → Produces a float score between 0.0 and 1.0

Step 7 — Filter by constraints
         → Budget filter (price ≤ input)
         → Location filter (within radius)
         → Rating threshold (≥ minimum rating)

Step 8 — Max-Heap insertion
         → Insert all scored candidates into a max-heap
         → Extract Top-K (e.g., top 5 or top 10) in O(K log n)

Step 9 — Merge Sort final list
         → Sort final results by composite score (similarity × rating × relevance)

Step 10 — Display Results
          → Show ranked restaurant cards with name, cuisine, price, rating, score
```

---

## 7. Module Breakdown

| Module | File | DSA |
|---|---|---|---|
| Search / Autocomplete | `trie.py` | Trie |
| User Profile Store | `profile_store.py` | HashMap |
| Restaurant Data Store | `restaurant_store.py` | HashMap |
| Similarity Graph | `graph.py` | Graph |
| Graph Traversal | `traversal.py` | BFS + Dijkstra |
| Scoring Engine | `scorer.py` | Cosine Similarity |
| Ranking Engine | `ranker.py` | Max-Heap + Merge Sort |
| Mock Data | `data/restaurants.json` | — |
| Main Entry Point | `main.py` | — |
| Web UI (optional) | `app.py` | — |

---

## 8. Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Language | Python 3.11+ | Easy DSA implementation, great for demos |
| Data Format | JSON | Simple mock restaurant dataset |
| CLI Interface | Python `input()` / `argparse` | No setup needed, easy to demo |
| Web UI (optional) | Streamlit | Build a clean UI in pure Python, no HTML/CSS needed |
| Visualization | Matplotlib / NetworkX | Draw the restaurant graph for presentation |
| Version Control | Git + GitHub | Team collaboration |
| Testing | pytest | Unit test each DSA module |

**No database needed** — all data is loaded from JSON into memory using hash maps at startup.

---

## 9. Folder Structure

```
restaurant-recommender/
│
├── data/
│   └── restaurants.json        # Mock dataset of 50-100 restaurants
│
├── modules/
│   ├── trie.py                 # Trie for autocomplete
│   ├── graph.py                # Restaurant similarity graph
│   ├── traversal.py            # BFS + Dijkstra
│   ├── scorer.py               # Cosine similarity scoring
│   ├── ranker.py               # Max-heap + merge sort
│   ├── profile_store.py        # User profile hash map
│   └── restaurant_store.py     # Restaurant data hash map
│
├── tests/
│   ├── test_trie.py
│   ├── test_graph.py
│   ├── test_scorer.py
│   └── test_ranker.py
│
├── app.py                      # Optional Streamlit web UI
├── main.py                     # CLI entry point
├── requirements.txt
└── README.md
```

---

## 10. Mock Data Plan

Each restaurant in `restaurants.json` will have:

```json
{
  "id": "R001",
  "name": "Spice Garden",
  "cuisine": ["Indian", "North Indian"],
  "tags": ["spicy", "vegetarian", "family"],
  "price_for_two": 400,
  "rating": 4.3,
  "location": "Koramangala",
  "feature_vector": [0.9, 1.0, 0.4, 4.3]
}
```

**Feature vector format:** `[spice_level, veg_friendly, price_normalized, rating_normalized]`

We will create 50–80 restaurants across 5–6 cuisines (Indian, Chinese, Italian, Mexican, Continental, Fast Food).

---

## 11. Build Phases & Tasks

### Phase 1 — Data & Foundation (Day 1–2)
- [ ] Create `restaurants.json` with 50+ entries
- [ ] Build `restaurant_store.py` (HashMap loader)
- [ ] Build `profile_store.py` (User profile HashMap)

### Phase 2 — Core DSA Modules (Day 3–5)
- [ ] Build `trie.py` (Insert + search + autocomplete)
- [ ] Build `graph.py` (Add nodes, add edges, adjacency list)
- [ ] Build `traversal.py` (BFS + Dijkstra)
- [ ] Build `scorer.py` (Cosine similarity)
- [ ] Build `ranker.py` (Max-heap + merge sort)

### Phase 3 — Integration (Day 6–7)
- [ ] Build `main.py` connecting all modules
- [ ] Test end-to-end flow with sample inputs
- [ ] Write unit tests in `tests/`

### Phase 4 — UI & Polish (Day 8–9)
- [ ] Build Streamlit `app.py` (optional but great for demo)
- [ ] Add graph visualization with NetworkX
- [ ] Polish output formatting

### Phase 5 — Presentation Prep (Day 10)
- [ ] Prepare slides showing each DSA with diagrams
- [ ] Record a demo walkthrough
- [ ] Prepare complexity analysis table

---