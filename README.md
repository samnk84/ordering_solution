# FIXR Technical Test

## Preamble

You are in charge of the API of a company that sells tickets for many events which is used by the companies mobile and web application.
The API, so far, is pretty simple, frontend applications can :
- list / retrieve the detail of all the events
- make a booking of x tickets of a given event's ticket type
- list / retrieve the details of their own booking


## Goal
### Cancellation feature

In order to make your head of product (and your customers - of course) happy, you have to build a new feature:
The users should now have the possibility to cancel any order within 30 minutes of purchase.

### Some metrics

Because of this new feature, the financial controller is on the edge of their chair, wanting to know the impact it will have on the company's profits.
In order to have a feel for it, he asked you to create a reusable piece of code to pull out two pieces of information:
   - The number of orders for a given event and its cancellation rate (as a percentage)
   - The date with the highest number of cancelled tickets (not orders! i.e: 1 order of 15 tickets > 14 orders of 1 ticket)


## Coding restrictions

None, really ! You are allowed to use whatever you feel is best to achieve your goals.


## Time limit

No real time limit. It's entirely up to you.
However, we highly suggest that you allocate yourself a set amount of time (ideally an hour) and do as much as you can during this time, then submit your results -
even if you haven't finished, it's fine, we know time is precious.


### Solution

I have added the desired logic into model classes, I have added new fields to help me build the solution and have 
added comments to identify them. I have not added the new fields to the serializer because we have not yet exposed them through an api. 
