h1 Assumptions

"Top Writers by Average Rating" can be interpreted two ways:
-The mean rating of all reviews associated with an author.
-The mean rating of all books associated with an author.

I'm going with the former, more literal definition (frankly because it's easier not to have to keep track 
of author/book pairs). In a real setting I think the latter definition is better since it doesn't 
confound quality and popularity, and we should try to extract single, independent factors where we can. 
Obviously, this is up to the stakeholders and the point would be to clarify rather than assume. 

I'm assuming we don't need to capture the raw data.

I'm also going to assume that 10 years is a reasonable lifetime before a planned upgrade.

------------------------------- Data -------------------------------------

Rough, back of the napkin calculation on how much data we're dealing with:
100mb == 50k records
10GB == 5 million records
== 36.5TB over 10 years

compacts to about 1MB for 50K
or 100MB a day
Which is 360gb over 10 years of storage.

It's worth noting that many of the author names are in UTF-8 non-English characters, 
this need to be maintained to avoid skewing the data towards Anglo-centric results.
We will need to keep this in mind when presenting the data to the user or other services.

We could encode the UTF-8 for better backwards compatibility, but since it’s a greenfield project
we may as well just support the correct format.

------------------------------- Design ------------------------------------

This is a pretty asymmetrical pipeline: we're doing non-trivial processing on the 
data at ingress, while the responsiveness is all we care about at read time. 
These operations will also scale more or less independently as we add more data or more 
users, so it's definitely worth using a Command Query Responsibility Separation (CQRS) pattern.

From the pattern we then want to simplify where possible and make sure we decouple anything that 
we have a high chance of changing if circumstances change. 

In this case the data is simple enough that we don't need separately synced read and write databases,
so we'll just use a single database. We'll add a DataModel abstraction to allow for this to change if
there's significant asymmetrical scaling in the future. 

Command Pipeline
API -> Data Ingress -> MessageQ -> Averager -> DataModel -> DB

Query Pipeline
API <- DataModel <- DB


-------------------------------- Efficiency ------------------------------------

Processing efficiency 
Process takes >10s using pandas or <2s manually
This should average out to about 200s of CPU time a day.
We could replace this with a C# implementation, which could well be faster but the 
data doesn't seem like it needs to be updated in real time so we'll defer any serious optimisation.
