// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract ZenID is ERC721URIStorage {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIds;

    struct Profile {
        string username;
        string avatar; // IPFS CID or URL
    }

    struct Status {
        string content;
        uint256 timestamp;
        uint256 likes;
    }

    mapping(address => Profile) public profiles;
    mapping(address => Status[]) public userStatuses;
    mapping(address => mapping(address => mapping(uint256 => bool))) public liked;
    mapping(address => mapping(address => bool)) public following;
    mapping(address => uint256) public reputation;
    mapping(address => uint256) private userTokenId;

    event ProfileCreated(address user, uint256 tokenId, string username);
    event ProfileUpdated(address user, string username, string avatar);
    event StatusPosted(address user, string content, uint256 timestamp);
    event StatusLiked(address liker, address author, uint256 index);
    event Followed(address follower, address target);
    event Unfollowed(address follower, address target);

    constructor() ERC721("ZenID Profile", "ZENID") {}

    // Mint NFT profile
    function createProfile(string memory username, string memory avatar, string memory tokenURI) public {
        require(bytes(profiles[msg.sender].username).length == 0, "Profile already exists");

        _tokenIds.increment();
        uint256 newId = _tokenIds.current();
        _mint(msg.sender, newId);
        _setTokenURI(newId, tokenURI);

        profiles[msg.sender] = Profile(username, avatar);
        userTokenId[msg.sender] = newId;

        emit ProfileCreated(msg.sender, newId, username);
    }

    // Update profile info
    function updateProfile(string memory username, string memory avatar, string memory tokenURI) public {
        require(bytes(profiles[msg.sender].username).length > 0, "No profile yet");

        profiles[msg.sender] = Profile(username, avatar);
        uint256 tokenId = userTokenId[msg.sender];
        _setTokenURI(tokenId, tokenURI);

        emit ProfileUpdated(msg.sender, username, avatar);
    }

    // Get profile info
    function getProfile(address user) public view returns (string memory, string memory, uint256, uint256) {
        Profile memory p = profiles[user];
        return (p.username, p.avatar, reputation[user], userTokenId[user]);
    }

    // Post status
    function postStatus(string memory content) public {
        require(bytes(profiles[msg.sender].username).length > 0, "No profile yet");
        userStatuses[msg.sender].push(Status(content, block.timestamp, 0));
        emit StatusPosted(msg.sender, content, block.timestamp);
    }

    // Get all statuses
    function getStatuses(address user) public view returns (Status[] memory) {
        return userStatuses[user];
    }

    // Like a status
    function likeStatus(address author, uint256 index) public {
        require(index < userStatuses[author].length, "Invalid status index");
        require(!liked[msg.sender][author][index], "Already liked");

        liked[msg.sender][author][index] = true;
        userStatuses[author][index].likes += 1;
        reputation[author] += 1;

        emit StatusLiked(msg.sender, author, index);
    }

    // Follow user
    function follow(address target) public {
        require(target != msg.sender, "Cannot follow yourself");
        following[msg.sender][target] = true;
        emit Followed(msg.sender, target);
    }

    // Unfollow user
    function unfollow(address target) public {
        following[msg.sender][target] = false;
        emit Unfollowed(msg.sender, target);
    }

    // Check if following
    function isFollowing(address user, address target) public view returns (bool) {
        return following[user][target];
    }
}