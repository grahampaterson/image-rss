## Bugs
- add to git __DONE__
- If feed url is similar to existing url (trailing space, different url etc...) a new feed entry will be added but it will be unable to associate with any images because their urls already exist in the other feed. possible solution, just add duplicate url data but don't allow image duplicates of images with same feed_id __DONE__
- Improve removing small images (move server side?)
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

## Todos

- implement list of subs on screen with option to remove subs
- add to github??
- convert regular urls to rss urls
- confirm feed before adding to subscriptions
- Drag and drop interface for selecting active feeds
- Login system
- Loader while feed is adding
- Lazy load images if the user has a large amount of subs
- list of added feeds with a remove button
- add feed id to each image element so that I can manipulate active screen
- combine data from similar urls, or give option to select correct rss from similar urls
