# Building a National E-Auction Platform for 1.4 Million Users

*What happens when hundreds of people press "bid" at the exact same second, each thinking they're the only one smart enough to snipe the auction.*

---

A guy bids on a seized car listed at around 100,000 lira. He waits until the last second, presses the button, and wins. Except the price is now 300,000. He didn't expect that. He files a complaint: "I only wanted to raise it by one increment, cancel this."

We can't cancel it. Here's what happened: a hundred other people had the exact same idea. They all waited for the last second. They all pressed bid at the same time. Every single bid landed on the server within the same second, each one pushing the price up by one increment, processed in the order they arrived. His bid happened to be the last one through.

He thought he was being clever. So did everyone else.

This is the core engineering challenge behind a national e-auction platform I built for a government ministry. Not the scale, not the bank integrations, not the government authentication. The hard part was building a bidding engine that could process hundreds of simultaneous bids fast enough that a millisecond difference in arrival time determined the outcome.

## What the Platform Does

The platform runs the country's customs liquidation auctions. When goods are seized at customs, abandoned, or expire their storage period, they're sold through public auction. Cars, electronics, machinery, raw materials. Everything that enters the country through customs and doesn't get claimed eventually ends up here.

Before this platform, these auctions happened in physical rooms. Few people showed up, competition was low, prices stayed low. The electronic system opened it up to anyone in the country with an internet connection.

Around 1.4 million registered users. Roughly 15,000 auctions per year, with about 90% ending in a sale. Annual transaction volume hit 6 billion lira last year. Two engineers built this from scratch.

## Inheriting a Broken System

There was an existing system before us. It had been built internally with government resources and it showed. The UI and backend were tightly coupled in a classic server-rendered setup. No mobile support. Frequent errors that users had just learned to live with. The codebase had grown beyond what the original team could manage, and adding new features meant fighting the architecture at every step.

A friend and I took the project over. He handled the frontend and mobile apps. I built the entire backend. Two people, under six months, replacing a live system that served over a million users.

## The Architecture

The backend runs on .NET Core, containerized with Docker. Four backend instances behind a load balancer, with SQL Server as the database. Redis handles caching for session data, active auction state, and bid queues. The kind of hot data you can't afford to hit the database for on every request. Auction photos, vehicle inspections, and expert reports are stored in MinIO using the S3 protocol.

There's also an internal administration module, separate from the public-facing system. Auction officials use it to create listings, set base prices, start and end auctions, review results. It's invisible to the outside world.

The user-facing side runs on two protocols. REST APIs handle authentication, search, and account management. Everything that's request-response in nature. WebSocket connections handle the real-time parts: live bid updates, auction countdowns, dashboard feeds. When an auction is in its final minutes and hundreds of people are watching the same item, you need push, not poll.

## Bank Integrations and the Deposit System

Before you can bid on anything, you need money in the system. The platform holds user deposits as a free balance that gets debited when you bid and credited back when you lose.

Users deposit money through their regular internet banking apps. Not a wire transfer where you type in an account number and a reference. The government entity appears as an institutional payee in the banking app's menu. You select it, enter the amount, confirm. Four of the country's leading banks support this.

On our side, the bank integration runs as a separate service. When a deposit comes through, the bank calls our SOAP endpoint with the user's identity and the amount. The money shows up in the user's free balance in real time. At the end of each day, there's an automated reconciliation process. The bank sends a summary: "We forwarded X requests totaling Y lira today." Our system checks its records independently: "We received X requests totaling Y lira." If the numbers don't match, the system flags it automatically. You don't get to be sloppy with public money.

## Identity and Authorization

All logins go through Turkey's national e-Government gateway using OpenID Connect. No separate username/password system. If you can log into the gateway, you can log into the auction platform.

The more interesting problem was corporate authorization. In the old system, if you wanted to bid on behalf of a company, you had to submit paperwork (signature circulars, trade registry documents) and someone had to manually verify and flag your account. You can guess what went wrong: when someone lost their authority to represent a company, nobody knew until someone checked. The account stayed active.

We pulled company authorization data directly from the national commercial registry. Every time a user logs in, we query which companies they're authorized to represent. Right now, in real time. If you were removed from a company's board yesterday, you can't bid on their behalf today. The system asks at login: "Do you want to enter as an individual or on behalf of [company name]?" Only companies where you have current, verified authority show up in that list.

## The Bidding Engine

An auction runs for a set period. Most of the time, nothing happens. People browse, check the inspection photos, read the expert report. Maybe a few bids trickle in early, testing the waters. The base price is set by the commission, and the opening bid starts at 50% for goods and 75% for vehicles.

Then the last few minutes arrive, and everything changes.

Everyone wants to be the last bidder. The logic is simple: if you bid early, someone will outbid you. If you bid at the last possible second, maybe nobody has time to respond. Hundreds of users are watching the same auction, fingers hovering over the bid button, waiting for the clock to tick down.

When the auction enters its final seconds, the server gets hit with a wall of bids. Sometimes fifty or more within the same second. Each bid needs to be validated (does this user have enough balance? is this bid higher than the current highest?), processed, and the result pushed to every connected client, all before the next bid in the queue.

The ordering is straightforward: bids are processed in the order they arrive at the server. First in, first processed. If two bids arrive at the same millisecond, the one that hits the server's network stack first wins. Your internet connection speed matters. Your proximity to the data center matters. It's a race, and the server is the finish line.

There's a critical rule: **you cannot outbid yourself.** If you're currently the highest bidder, pressing the bid button does nothing. You have to wait for someone else to outbid you first. Simple rule, but it changes everything. No panic-clicking. You can't just hammer the button and accidentally drive the price up against yourself.

## Designing Against Collusion

People get creative when real money is on the table.

Here's a scheme we had to prevent. Say an item has a base price of 500,000 lira. Person A and Person B agree to work together. Person A bids, pushing the price to 505,000. Then Person B comes in and bids it up to 1,000,000. Nobody else bids because the price is now absurdly high. The auction ends. Person B "wins" at 1,000,000 but doesn't pay. Their deposit (10% of the sale price, so 100,000) gets forfeited, and the item passes to the second-highest bidder, Person A, at 505,000. They just got a 500,000-lira item for 505,000 plus their friend's 100,000 in forfeited deposit. Total: 605,000. If the item would have normally gone for 800,000 or 900,000 in honest bidding, they've saved a significant amount.

To prevent this, we implemented a maximum bid increment limit. You can't jump the price by an arbitrary amount. Each bid can only raise the price by a fixed increment, ranging from 50 to 2,000 lira depending on the item's value. You want to double the price in one bid? The system won't let you. You'd have to click hundreds of times, and by then, other bidders have time to react.

## The Auto-Bid Engine

The obvious fix for last-second sniping would be to extend the auction clock when a bid comes in near the end. Many platforms do this. We considered it. But auction durations aren't up to us. Listing durations, bidding windows, settlement deadlines are all defined in legislation. We couldn't change the clock, so we had to build something else.

Honestly, the ideal setup would be both. Auto-bid combined with a rule like "if a bid comes in during the last five minutes, extend by five more" would make sniping almost pointless. The extension gives everyone time to react, and auto-bid means you don't even have to be there. Together they'd cover each other's gaps. But we could only build one of them.

That one was auto-bid.

Users can activate auto-bidding on any item. You set two parameters: the increment amount and your maximum price. Once activated, whenever someone outbids you, the system automatically places a new bid on your behalf at your chosen increment. It keeps going until either you're the highest bidder or the price exceeds your maximum.

Before auto-bid, you had to be glued to your screen in the final seconds, pressing the button at exactly the right moment. Now you set your limit and walk away.

It gets fun when two auto-bids go head to head. Say User A has auto-bid active with a max of 800,000 and User B has a max of 600,000, both on the same item sitting at 400,000. A manual bid comes in at 405,000. User A's auto-bid fires, pushing to 410,000. User B's auto-bid responds, 415,000. They go back and forth automatically until User B's limit is reached at 600,000. User A's auto-bid places one final bid at 605,000 (one increment above B's maximum) and stops. It doesn't keep climbing to 800,000. It parks at the minimum needed to win and waits for the next challenger.

A sniper shows up at the final second, presses bid, expects to win at a low price. Instead, the auto-bid engine immediately fires back, raising the price. The sniper sees their bid confirmed but they're already outbid. If there are multiple auto-bids active, the price can double or triple in that final second, which is exactly what surprises those users who call in to complain: "I pressed bid once and somehow I'm paying three times what the price was."

You pressed bid once. So did a hundred other people. And the auto-bid engine was already there waiting for all of you.

When we first launched auto-bid, some users didn't fully understand it and got burned. But once people figured it out, it became the feature they liked most. Some snipers lost their edge, which they weren't happy about. But for most users, it meant you no longer needed to be glued to your phone at the exact right second. You just needed to know what something was worth to you.

## Going Live Too Early

The decision to go live came faster than we expected. Testing wasn't fully complete, but the switch was flipped. The platform went live in a day.

Most things worked. The bank integrations didn't, at least not all of them. A couple of the bank connections had issues we hadn't caught because we hadn't finished end-to-end testing with real transactions. Deposits from those banks weren't coming through. We fixed it within a couple of days, but those were a rough couple of days.

Then came the surprise we really didn't plan for. Within hours of launch, we noticed the system slowing down in ways that didn't match the user count. We dug into the logs and found IPs generating massive amounts of requests. Millions of hits. Users had built bots.

In hindsight, it makes sense. People had been using the old system for years. Some of them had automated their bidding workflows and pointed their scripts at the new platform the moment it went live. We hadn't anticipated it because the old system apparently had the same problem and nobody told us.

We added rate limiting, tightened up the JWT token validation with extra checks to make bot simulation harder, and strengthened the caching layer, especially for the homepage and auction listings that bots were hammering. The bot traffic dropped to a fraction of what it was. We should have seen it coming. If people are willing to build bots for sneaker drops, of course they'll build them for government auctions where you can buy a car below market price.

## What I Took Away

**Design for human behavior, not just technical requirements.** The hardest problems weren't about throughput or latency. They were about people trying to game the system. Every anti-cheating rule (bid increment limits, auto-bidding, the you-can't-outbid-yourself constraint) exists because someone tried something clever and we had to respond.

**Real-time financial systems need reconciliation.** It's not enough that deposits arrive. You need to verify, independently, at the end of every day, that what the bank says matches what your system recorded. Public money doesn't do "close enough."

**Government integrations eliminate categories of fraud.** Pulling company authorization from the national commercial registry in real time instead of trusting paper documents closed a hole that had been open for years. Every time you can replace a manual verification with a live system query, you should.

**Two engineers can replace a legacy system if the scope is clear.** We didn't build a generic auction platform. We built this specific auction platform, for this specific workflow, with these specific rules. Knowing exactly what we needed to build, and more importantly what we didn't, is what made it possible with a team of two.

---

*I'm Burak Hamuryen, a Senior Software Engineer in Berlin with 14+ years of experience building distributed systems, real-time video processing, and cloud-native platforms. More at [hamuryen.com](https://hamuryen.com).*

---

## Further Reading

- [Auction Sniping (Wikipedia)](https://en.wikipedia.org/wiki/Auction_sniping) - the game theory behind last-second bidding and why it's a rational strategy
- [Scaling WebSockets with Redis Pub/Sub](https://redis.io/docs/latest/develop/interact/pubsub/) - the pattern behind broadcasting real-time bid updates across multiple backend instances
- [OpenID Connect Specification](https://openid.net/developers/how-connect-works/) - the protocol we used for e-Government authentication
