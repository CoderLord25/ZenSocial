# 🪪 ZenID – SocialFi Identity dApp

ZenID is a decentralized **SocialFi application** built on the **ZenChain testnet**, powered by **NFT-based identities**.  
It acts as a **“passport”** for users in the ZenChain ecosystem, enabling them to own a verifiable on-chain identity and participate in social interactions (statuses, likes, follows) transparently.

---

## 📌 Overview

- **Problem solved:** Lack of trusted, verifiable digital identities on blockchain-based social platforms.  
- **Solution:** ZenID issues **NFT identities** to each user, making profiles tamper-proof and fully owned by the individual.  
- **Highlights:**
  - Decentralized Identity (DID) + NFT
  - On-chain profiles (username, avatar, metadata)
  - SocialFi interactions: status posts, likes, follows
  - Transparent reputation tracking

---

## 🏗 Architecture

- **Smart Contract (Solidity, ZenChain Testnet):**  
  Defines logic for minting NFT identities, updating profiles, posting statuses, liking, and following.  

- **NFT Identity Contract:**  
  Each user mints exactly one NFT that represents their digital identity. Metadata includes username, avatar, and IPFS URI.  

- **Frontend (HTML + JS + Ethers.js):**  
  Simple web interface where users can connect their wallet and interact with ZenID features.  

- **Wallet (ZenChain Wallet):**  
  Used to connect, sign, and confirm all blockchain transactions.

👉 **Interaction flow:**  
`User → Web dApp (UI) → Smart Contract → NFT Identity → SocialFi Features`

---

## ⚙️ Core Features

1. **Profile Creation (NFT Identity)**  
   - Mint a unique ZenID profile as an NFT (username, avatar, metadata).  

2. **Profile Management**  
   - Update profile details such as username, avatar, or metadata.  

3. **View Profiles**  
   - Load and display any user’s public information (username, avatar, reputation).  

4. **Post Status**  
   - Share short messages or updates directly on-chain.  

5. **Like Status**  
   - Engage with other users’ posts by liking their statuses.  

6. **Follow System**  
   - Follow/unfollow users to build an on-chain social graph.  

7. **Reputation Tracking**  
   - Reputation score increases as users receive likes, creating a measure of trust within the system.  

---

## 💻 Frontend Demonstration (Web Pages)

To complement the smart contract, a simple demo frontend was built with four pages:

- **Index Page:** Full interaction hub (create, update, view profiles, post status, like, follow/unfollow).  
- **Stats Page:** Displays personal statistics such as reputation, number of statuses, following, and followers.  
- **Explore Page:** Search for a user by address and view their public details (profile + reputation).  
- **Article Page:** Demo space to draft and publish longer content (proof-of-concept, off-chain in current version).  

---

## 🚀 Getting Started

### Prerequisites
- Node.js + npm
- Python + Flask (for serving the frontend locally)
- MetaMask or ZenChain Wallet


1. Clone the repo:
   ```bash
   git clone https://github.com/your-username/zenid.git
   cd zenid
 2. Install dependencies:
npm install
### Running the dApp
1. Start a local Flask server:
   flask run
2. Open your browser and navigate to:
   http://127.0.0.1:5000
3. Connect your wallet and start interacting with ZenID.
   
## 📂 Project Structure
  ZenID/
  │
  ├── ZenID.sol              # Deploy SmartContract ZenID
  ├── templates/             # Frontend HTML templates
  │   ├── index.html
  │   ├── stats.html
  │   ├── explore.html
  │   └── article.html
  ├── static/
  │   ├          # Frontend logic (Ethers.js integration)
  │   └── images/            # Project images (backgrounds, logo)
  ├── app.py                 # Flask backend to serve templates
  └── README.md              # Project documentation

## 📝 Conclusion
ZenID provides a minimal but complete SocialFi prototype:
1. On-chain NFT identities
2. Immutable profiles and posts
3. Social interactions (likes, follows)
4. Transparent reputation layer
--> This foundation demonstrates how NFT identities can extend beyond collectibles into functional applications, powering the next generation of decentralized social platforms

