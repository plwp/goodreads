# goodreads
Goodreads Kaggle Challenge

## Usage

This example runs within docker containers orchestrated by docker-compose which are both requirements.

To run the example first use:

`docker-compose build`

then:

`docker-compose up --scale averager=[n]` where [n] is the number of averager instances to spawn.

Wait for the RabbitMQ to be booted (should take around 10-15 seconds)

To upload data run:

`python3 datasource.py [csv file]` where [csv file] is the input data (or by default the included goodreads.csv)

Then you can see the top authors by rating by running:

`python3 presentation.py [n]` where [n] is the number of results you want.

Note: It can take some time for all the results to appear, but the update is complete when Postgres stops warming the room via your CPU.

## Assumptions

"Top Writers by Average Rating" can be interpreted two ways:
1. The mean rating of all reviews associated with an author.
2. The mean rating of all books associated with an author.

Interpretation 1 would mean that the output is dependant on 2 factors of the book: quality and popularity, where as 2 is only dependant on quality. Normally it's better to favour single factors for analysis (you can always re-synthesise combined results). However to accurately track a book's avarage over time we'd need to store records on a per-book basis (because we may see an updated record for the same book over time and we don't want to measure it twice). The data storage requirements for this version. For this reason we're going to assume the first interpretation (although we'd obviously clarify this with the stakeholders rather than assume).

Assume we don't need to capture the raw data.

Assume that 10 years is a reasonable lifetime before a planned upgrade (or implementing a rolling average of the data).

Assume that ratings for books with multiple authors apply to each co-author of the book.

Assume that we're not working with real-time requirements.

## Data

Rough, back of the napkin calculation on how much data we're dealing with:
Throughput:
- 100mb == 50k records
- 10GB == 5 million records
- 36.5TB over 10 years

Storage
- Compacts to about 1MB for 50K
- 100MB a day
- 360gb over 10 years of storage.

It's worth noting that many of the author names are in UTF-8 non-English characters, this need to be maintained to avoid skewing the data towards Anglo-centric results. We will need to keep this in mind when presenting the data to the user or other services. We could encode the UTF-8 for better backwards compatibility, but since it’s a greenfield project we may as well just support the correct format.

## Scope

This repository will focus on a simple backend-API implementation of the design using docker-compose for container orchestration and deployment.

In order to keep the deployment as simple as possible we're avoiding any build scripts and keeping everything we need within the repository.

This means there's some bad practice (splitting the DataModel into different folders), and some terrible practice (uploading passwords and private keys to github). This is to keep deployment as simple as possible.

The Data Source and Presentation services have been implemented as python stubs, as have the Authentication and Data Ingress services discussed in the design powerpoint.

## Design

This is a pretty asymmetrical pipeline: we're doing non-trivial processing on the data at ingress, while the responsiveness is all we care about at read time. These operations will also scale more or less independently as we add more data or more users, so it's definitely worth using a Command Query Responsibility Separation (CQRS) pattern.

From the pattern we then want to simplify where possible and make sure we decouple anything that we have a high chance of changing if circumstances change. In this case the data is simple enough that we don't need separately synced read and write databases, so we'll just use a single database. We'll add a DataModel abstraction to allow for this to change if there's significant asymmetrical scaling in the future. 

Command Pipeline
API -> Data Ingress -> RabbitMQ -> Averager|DataModel ->  DB

Query Pipeline
API|DataModel <- DB

## Future Work / Issues

Issues:
- In order to easily split the DataModel code we're using dicts instead of Classes, which would definitely be better practice.
- Database access is definitely the biggest bottleneck. In the end I went with copping the hit to memory to reduce the number of transactions, but there's definitely a better way to be doing it that doesn't kill the speed. I'd definitely want to get some ideas from someone with strong DB expertise. The other option would just be to switch to a non-relational solution. As a proof of concept it's fine but it's definitely something that would need fixing. By fixing this issue we can expect a 15x speedup.
- Even without real time requirements improving CPU and memory efficiency will cut down on costs.


