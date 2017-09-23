## Bugs
- add to git __DONE__
- If feed url is similar to existing url (trailing space, different url etc...) a new feed entry will be added but it will be unable to associate with any images because their urls already exist in the other feed. possible solution, just add duplicate url data but don't allow image duplicates of images with same feed_id __DONE__
- Improve removing small images (move server side?) Run through all images in database and remove small ones periodically??
- Run through subscriptions and delete all subscriptions that no longer have a user
- Fix isotope
- Update user cookie date on landing
- create new cookie on landing if current cookie doesn't exist on the server __DONE__
- More error reporting to find Bugs
- Check out the disabled ssl certification??
- limit subscriptions to one feed per user __DONE__
- Update the add interface so it doesn't add duplicates __DONE__
- Fix Sorting
- When adding a url get the redirected source url rather than the entered url
- modify add feed to get data from server instead of clientside __DONE__
- Figure out why memory use is so high

## Todos

- Update feeds automatically each day
- implement list of subs on screen with option to remove subs __DONE__
- when removing subs remove them from the active page __DONE__
- add to github??
- convert regular urls to rss urls
- confirm feed before adding to subscriptions
- Drag and drop interface for selecting active feeds
- Login system
- Loader while feed is adding
- Lazy load images if the user has a large amount of subs
- list of added feeds with a remove button __DONE__
- add feed id to each image element so that I can manipulate active screen __DONE__
- combine data from similar urls, or give option to select correct rss from similar urls
- Add hover state to cards with website url a la pinterest
- Make links open in new window for grid items
- Add timestamped logging to file
