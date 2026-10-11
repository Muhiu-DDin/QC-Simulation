"""Evidence-backed audit records. No credentials or authentication values are included."""
from pathlib import Path
from collections import Counter
import csv
import json
import hashlib
import math

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output' / 'forevermart-audit'
BASE = 'https://forevermart.vercel.app'
PRODUCT = '/product/68ee7c73675d613eba9e96c6'
JACKET = '/product/68f38f15f780484273055b41'
API = 'https://foreverbackend-k8zm.onrender.com/api'
records = []

def add(title, module, category, severity, route, steps, expected, actual, impact, remedy, retest, evidence, classification='Defect', method='Browser test', note=''):
    n = len(records) + 1
    owner = ('Backend developer' if module in ('Order API', 'Cart API', 'Account API') else
             'Content owner' if category == 'Content' else
             'Platform developer' if category == 'Security' and classification == 'Observation' else 'Frontend developer')
    records.append(dict(id=f'FM-{n:03d}', test_id=f'TC-{n:03d}', title=title, module=module,
        category=category, severity=severity, priority={'High':'P1','Medium':'P2','Low':'P3'}[severity],
        classification=classification, method=method, url=API+route if module.endswith('API') else BASE+route,
        preconditions=('Authenticated disposable demo account; cash on delivery; no real payment.' if module.endswith('API') or module in ('Orders','Checkout') else 'Public deployment available; use the stated page and test data.'),
        steps=steps.split(' | '), expected=expected, actual=actual, impact=impact, remedy=remedy,
        retest=retest, evidence=evidence.split(';'), note=note, status='Open' if classification=='Defect' else 'Review required',
        detected='2026-10-09', close_date='Not closed', build='Public deployment observed 9 October 2026',
        proposed_owner=owner, assigned_to='Not assigned', developer_comment='Not supplied', client_comment='Not supplied'))

# Public shopping and account journeys
add('Shop Now does not open the catalogue','Home','Functionality','Medium','/',
    'Open the home page. | Click SHOP NOW in the hero.',
    'The call to action opens the collection or another defined shopping destination.',
    'The URL and page remain unchanged; SHOP NOW is rendered as a paragraph without an action.',
    'The primary shopping invitation cannot be used.',
    'Render a real link to /collection with a visible focus state.',
    'Mouse click and Enter on the focused link both open Collection.', 'evidence/shop-now-no-action.json;evidence/shop-now-no-action.jpg;raw/app.js')
add('Best Seller section has no products despite flagged catalogue items','Home','Functionality','Medium','/',
    'Allow the catalogue to finish loading. | Inspect BEST SELLER and compare the public product flags.',
    'Products marked bestSeller are displayed in the section.',
    'The section is empty although five catalogue records have bestSeller=true. The public bundle filters the different key bestseller.',
    'Merchandising content disappears and an empty section occupies the home page.',
    'Use the product contract key bestSeller and map productName consistently. Add a populated-fixture component check.',
    'The five flagged records render with names and prices; an empty source has a deliberate empty state.', 'evidence/home-desktop.jpg;raw/products.json;raw/app.js', method='Browser test and public code review')
add('Latest Collection is not ordered by creation date','Home','Content','Low','/',
    'Inspect the ten Latest Collection items. | Compare their createdAt values with the full public catalogue.',
    'A section labelled Latest Collection presents the newest products first, or explains its curation.',
    'The list takes the first ten API records. An October 14 record leads the list while newer October 22 records are available.',
    'The section title does not describe its actual selection.',
    'Sort a copy of products by createdAt descending before taking ten, or rename the section Featured Collection.',
    'A fixture containing older and newer products displays the declared ordering.', 'raw/products.json;raw/app.js;evidence/home-desktop.jpg', classification='Observation', method='Public data and code review', note='Latest is an inferred merchandising criterion; confirm with the owner.')
add('Reviews tab does not display reviews','Product','Functionality','Medium',PRODUCT,
    'Open the product and allow its data to load. | Click Reviews (122).',
    'The selected tab displays the reviews or an honest unavailable state.',
    'The displayed content does not change; the tab is a paragraph without a click handler.',
    'Customers cannot inspect the reviews advertised by the page.',
    'Implement accessible tabs backed by review data, or remove the inactive review tab and count.',
    'Selecting Reviews changes the panel; keyboard selection works and the empty state is truthful.', 'evidence/reviews-no-change.jpg;raw/app.js')
add('Product rating and review count are hard coded','Product','Content','Medium',PRODUCT,
    'Open the cotton T-shirt. | Open the Women Zip-Front Jacket and compare the rating area with the public data and bundle.',
    'Rating and count derive from actual product reviews, or are clearly identified as sample content.',
    'Both display the same stars and (122); these values are fixed in the public component and not derived from review data.',
    'The storefront presents unsupported customer-feedback claims.',
    'Aggregate approved reviews by product. Hide ratings when no verified review source exists; label demo fixtures explicitly.',
    'Products with zero, one and several reviews show the correct counts and calculated ratings.', 'evidence/product-details.json;evidence/second-product-loaded.json;raw/app.js', method='Browser test and public code review')
add('Jacket description describes a short sleeved T-shirt','Product','Content','Medium',JACKET,
    'Open Women Zip-Front Relaxed Fit Jacket priced $399. | Read the short product description.',
    'The description explains the jacket actually offered.',
    'The jacket uses a generic round-neck, short-sleeved pullover shirt description. The same text is reused across different apparel types.',
    'Customers receive incorrect information about the item.',
    'Replace copied descriptions with product-specific material, fit, closure and care details; validate catalogue content before publishing.',
    'Jackets, trousers and tops each have accurate descriptions matching their records and images.', 'evidence/second-product-loaded.json;evidence/second-product-loaded.jpg;raw/products.json')
add('Detailed Description panel explains ecommerce instead of the product','Product','Content','Low',PRODUCT,
    'Open the product. | Read the Description panel below the purchase controls.',
    'The panel contains useful details about this product.',
    'The text explains what an ecommerce website is rather than describing the selected apparel.',
    'A prominent information panel gives customers no product details.',
    'Populate the panel from a product detail field; remove template instructional copy.',
    'Changing product changes the details and no ecommerce-definition template text remains.', 'evidence/product-details.json;raw/app.js')
add('Product image and title describe different garment styles','Product','Content','Medium',PRODUCT,
    'Open Men Round Neck Pure Cotton T-shirt priced $200. | Compare the main photo with the title and description.',
    'The images depict the named round-neck, short-sleeved T-shirt.',
    'The main photo depicts a pink collared, long-sleeved shirt while the title and description describe a round-neck T-shirt.',
    'The shopper cannot reliably determine which garment will be delivered.',
    'Correct the product-to-image association or the product text after checking the intended inventory item.',
    'All gallery images match the approved product identity and garment characteristics.', 'evidence/product-details.jpg;evidence/product-details.json;raw/products.json')
add('Related Products includes the product already being viewed','Product','Functionality','Low',PRODUCT,
    'Open the $200 T-shirt. | Inspect Related Products.',
    'Recommendations provide other relevant items.',
    'The current product appears in its own related-product list; the filter does not exclude the current ID.',
    'A recommendation slot is wasted on an item already open.',
    'Exclude the current product ID before limiting related results.',
    'No related result has the current ID, including after navigation between related items.', 'evidence/product-details.json;raw/app.js', method='Browser test and public code review')
add('Selected size carries over when navigating to a related product','Product','Functionality','Medium',PRODUCT,
    'Choose size M on the $200 T-shirt. | Open a related product priced $280. | Inspect the size selection before choosing a size again.',
    'The new product starts with no selection, or explicitly asks the customer to confirm its variant.',
    'M remains selected on the new product even though it was selected for the previous item.',
    'A shopper can add the next item using an unintended variant.',
    'Reset variant and gallery state whenever productId changes; validate the selected size against the new product.',
    'Navigate between products with different size lists; adding requires a valid selection for the new item.', 'evidence/related-size-carryover.json;evidence/related-size-carryover.jpg')
add('Unknown product leaves an incomplete purchase page','Product','Functionality','Medium','/product/000000000000000000000000',
    'Open the stated non-existent product ID. | Allow the request to complete.',
    'A Product not found state replaces purchase controls and offers a route back to the collection.',
    'The page shows an empty title, a currency symbol without a price, hard-coded review content and ADD TO CART.',
    'A broken URL looks like a purchasable item rather than a handled missing record.',
    'Track loading, found, missing and failed states; render purchase controls only for a valid product.',
    'Missing and malformed IDs have a clear recovery page; valid products still load normally.', 'evidence/missing-product.json;evidence/missing-product.jpg')
add('Search with no matches displays an unexplained empty grid','Collection','Usability','Medium','/collection',
    'Open search on Collection. | Enter zzqa-no-such-product.',
    'A no-results message identifies the search and offers a clear or reset action.',
    'No product cards appear and no no-results explanation is displayed.',
    'Users cannot distinguish an empty result from a failed load.',
    'Render a no-results state after loading completes, with a clear-search action.',
    'An impossible query shows the message; clearing it restores products.', 'evidence/search-no-results.json;evidence/search-no-results.jpg')
add('Leading and trailing spaces prevent otherwise valid search matches','Collection','Functionality','Medium','/collection',
    'Search for cotton. | Replace it with two leading spaces, cotton, and two trailing spaces.',
    'Incidental outside whitespace does not change the meaningful query.',
    'cotton finds 22 items, while the padded query finds none. The filter lowercases text but does not trim it.',
    'Pasted or casually typed queries produce false empty results.',
    'Normalize the search with trim and consistent case handling before filtering.',
    'cotton, Cotton and padded cotton return the same matching IDs.', 'evidence/search-spaces.json;evidence/search-spaces.jpg;raw/app.js', method='Browser test and public code review')
add('Collection filters and sorting are lost after returning from a product','Collection','Functionality','Medium','/collection',
    'Select Men and Sort by Low to High. | Open a product. | Use browser Back.',
    'The previous collection criteria are restored.',
    'Men is unchecked and sorting returns to Relevant; all products are shown.',
    'Customers must repeat their selection after every product inspection.',
    'Store search, category and sort criteria in URL parameters or durable route state.',
    'Back restores the same criteria and results, and a shared filtered URL opens the same view.', 'evidence/collection-criteria.json;evidence/collection-after-back.json')
add('Footer navigation labels cannot be opened','Shared layout','Functionality','Medium','/',
    'Go to the footer. | Attempt Home, About Us, Delivery and Privacy Policy.',
    'Each advertised navigation destination is an operable link.',
    'All four labels are static list items with no href or action.',
    'Customers cannot reach the pages promised by the footer.',
    'Create valid links and publish the intended delivery and privacy content. Grouped here because the same footer implementation affects all four labels.',
    'All four destinations work with mouse and keyboard and have meaningful URLs.', 'evidence/home-mobile.json;raw/app.js')
add('Forgot your password has no recovery action','Account','Functionality','Medium','/login',
    'Open the account form. | Click Forgot your password?',
    'A recovery flow or a clearly explained support alternative opens.',
    'The page stays unchanged; the text has a pointer cursor but no handler.',
    'A user who has forgotten a password has no advertised recovery path.',
    'Implement a verified recovery process, or replace the inactive control with an accurate support instruction.',
    'The control opens recovery; account existence is not disclosed by recovery responses.', 'evidence/forgot-password-no-action.json;evidence/forgot-password-no-action.jpg;raw/app.js')
add('My Profile menu item has no destination','Account','Functionality','Medium','/',
    'Sign in with the disposable account. | Open the profile menu and click My Profile.',
    'The profile page opens or the unavailable feature is not presented as an action.',
    'No page or panel opens; My Profile is static text.',
    'The account menu advertises a function users cannot use.',
    'Link to an implemented profile page or remove the inactive menu item until available.',
    'Selecting My Profile opens a working destination with the authenticated demo profile.', 'evidence/profile-no-action.json;evidence/profile-no-action.jpg')
add('Explore Jobs does not open career information','Contact','Functionality','Low','/contact',
    'Open Contact. | Click Explore Jobs.',
    'The button opens career details or a supported application destination.',
    'The page and URL remain unchanged.',
    'The careers call to action is nonfunctional.',
    'Provide an actual careers link, or remove the button when no vacancies or careers page exist.',
    'Mouse and keyboard activation open the declared destination.', 'evidence/jobs-no-action.json;evidence/jobs-no-action.jpg;raw/app.js')
add('Newsletter subscription produces no result','Home','Functionality','Medium','/',
    'Enter a syntactically valid synthetic email in Subscribe now. | Click SUBSCRIBE.',
    'The form records the request and shows success or a useful error.',
    'There is no feedback or subscription action. The handler only prevents the default form submission.',
    'The advertised 20 percent offer has no usable subscription path.',
    'Connect the form to the intended subscription service and show a result; remove the offer until its fulfilment works.',
    'Valid, duplicate and invalid requests produce truthful, accessible feedback without unintended subscriptions.', 'evidence/subscribe-no-feedback.json;evidence/subscribe-no-feedback.jpg;raw/app.js', method='Browser test and public code review')
add('Product names are absent from cart and order rows','Cart','Functionality','Medium','/cart',
    'Add the $200 T-shirt in size M. | Inspect its cart row, then the own demo order history.',
    'Each row identifies the product by its stored productName.',
    'Images, price and size appear but the product name is blank. These views read name while records contain productName.',
    'Customers cannot clearly identify line items; the same data-contract mismatch affects both views.',
    'Use one typed product contract and read productName in cart and order components.',
    'Names appear for all line items in both cart and order history.', 'evidence/cart-one-item.json;evidence/orders-validation-tests.json;raw/app.js', method='Browser test and public code review')
add('Guest cart is overwritten after account creation','Cart','Functionality','High','/cart',
    'As a guest, add one item. | Create the disposable account. | Inspect the cart after authentication.',
    'The guest selection survives or is merged with the account cart.',
    'The badge changes from one item to zero and the guest item disappears when the empty account cart is loaded.',
    'A customer loses the prepared purchase at the authentication step.',
    'Merge validated guest items with the account cart on authentication and reconcile the result before replacing local state.',
    'Guest-only and existing-account carts merge without loss or duplicate quantities.', 'evidence/cart-one-item.json;evidence/signup-outcome.json;raw/app.js')
add('An empty cart can be submitted as an order','Checkout','Data integrity','High','/PlaceOrder',
    'Use the authenticated demo account with an empty cart. | Proceed to checkout, complete the delivery form and submit cash on delivery.',
    'Checkout is blocked when there are no valid line items; the server rejects an empty items array.',
    'Order creation succeeds and the own-orders response contains an order with items=[] and amount=10.',
    'Invalid transactions are stored and can enter fulfilment workflows. Empty orders are also invisible in the flattened history.',
    'Enforce non-empty validated items on the server and block the empty-cart checkout path in the UI.',
    'An empty order returns a validation error and creates no record; one valid item succeeds.', 'evidence/cart-empty.json;evidence/empty-order-outcome.json;raw/demo-orders.json')
add('Empty-cart total does not agree with displayed shipping','Cart','Functionality','Medium','/cart',
    'Open an empty cart. | Compare Subtotal, Shipping Fee and Total.',
    'Displayed amounts reconcile, and no charge applies to an order that cannot be placed.',
    'Subtotal is $0.00 and shipping $10.00, but Total is $0.00. An empty submitted order instead stores $10.',
    'The stated payable amount is internally inconsistent.',
    'Use one totals function across display and submission; hide or zero shipping for an empty cart.',
    'Empty and populated carts reconcile; submission and receipt equal the final displayed total.', 'evidence/cart-empty.json;evidence/cart-empty.jpg;raw/demo-orders.json')
add('Whitespace-only delivery information is accepted','Checkout','Data integrity','High','/PlaceOrder',
    'Enter three spaces in first name, last name, street, city, state and country; use a valid synthetic email. | Submit a demo COD order.',
    'Required address strings remain non-empty after trimming and are rejected otherwise.',
    'The order is accepted; the persisted address contains whitespace-only values.',
    'The stored order has no deliverable recipient or address.',
    'Trim and validate required strings on both client and server; show errors beside the fields.',
    'Each whitespace-only required field rejects the order without persistence; a valid address succeeds.', 'evidence/checkout-invalid-values.jpg;raw/demo-orders.json')
add('Negative phone number is accepted at checkout','Checkout','Data integrity','High','/PlaceOrder',
    'Complete other delivery fields and enter -1 for Phone number. | Submit the authorized demo COD test order.',
    'The contact field accepts a valid telephone string and rejects an impossible negative number.',
    'The server stores phoneNumber="-1".',
    'The fulfilment team has no usable delivery contact.',
    'Use type=tel and server-side phone validation appropriate to the supported countries; do not treat phone numbers as arithmetic quantities.',
    '-1 and malformed phones are rejected; supported formatted numbers remain intact.', 'evidence/checkout-invalid-values.jpg;raw/demo-orders.json')
add('Negative postal code is accepted at checkout','Checkout','Data integrity','Medium','/PlaceOrder',
    'Complete the other delivery fields and enter -1 for Zipcode. | Submit the authorized demo COD order.',
    'Postal codes are validated as country-appropriate identifiers.',
    'The persisted order contains zipCode="-1".',
    'The order can contain unusable delivery routing data.',
    'Use a text postal-code field and validate it against the selected supported country on the server.',
    'Negative values fail; valid supported numeric and alphanumeric codes pass.', 'evidence/checkout-invalid-values.jpg;raw/demo-orders.json')
add('Order endpoint accepts a malformed delivery email','Order API','Data integrity','Medium','/order/placeOrder',
    'Authenticate as the disposable account. | Submit one valid COD line item with address.email=not-an-email. | Fetch own orders.',
    'The server rejects a malformed email independently of browser validation.',
    'HTTP 200 success is returned and the malformed email persists in the order.',
    'API clients can create orders with unusable notification addresses.',
    'Apply the same validated address schema at the API boundary; return a field-specific 4xx error.',
    'Malformed email creates no order; a valid synthetic email passes.', 'raw/api-validation.json', method='Authenticated API test')
add('Order endpoint accepts a negative fractional quantity','Order API','Data integrity','High','/order/placeOrder',
    'Use the demo account and a valid product ID. | Submit quantity=-0.5 in a COD order. | Read back own orders.',
    'Every apparel quantity is a positive integer within the allowed limit.',
    'The endpoint returns success and persists -0.5; the history displays that quantity.',
    'Invalid units corrupt order and fulfilment calculations.',
    'Validate Number.isSafeInteger(quantity), quantity>=1 and a documented maximum before any write.',
    '-0.5, 0, fractional and excessive values fail; 1 and a valid upper bound pass.', 'raw/api-validation.json;evidence/orders-validation-tests.json', method='Authenticated API test')
add('Order endpoint accepts a size not sold for the product','Order API','Data integrity','High','/order/placeOrder',
    'Submit the valid T-shirt ID with size=QA-NOT-A-SIZE. | Fetch the resulting own order.',
    'The chosen size belongs to the server-side product variant list.',
    'HTTP 200 success is returned and QA-NOT-A-SIZE is stored and displayed.',
    'The order requests an impossible product variant.',
    'Resolve the product from the database and validate the requested variant against its current size list.',
    'Unknown sizes fail without persistence; supported sizes succeed.', 'raw/api-validation.json;evidence/orders-validation-tests.json', method='Authenticated API test')
add('Order endpoint accepts a non-existent product ID','Order API','Data integrity','High','/order/placeOrder',
    'Submit item ID 000000000000000000000000 with a copied valid product snapshot. | Fetch own orders.',
    'Every order line references an existing saleable server-side product.',
    'The fabricated ID is accepted and persisted.',
    'An order can reference inventory that does not exist.',
    'Look up every product and variant on the server; reject missing or unavailable records before writing the order.',
    'Non-existent IDs fail; existing allowed IDs succeed without trusting copied metadata.', 'raw/api-validation.json;raw/products.json', method='Authenticated API test')
add('Order endpoint trusts an altered client line-item price','Order API','Security','High','/order/placeOrder',
    'Copy the valid $200 T-shirt line. | Change its client price to 1 and submit amount=11. | Fetch own orders.',
    'The server uses its own catalogue price, ignoring a submitted client price.',
    'The order stores the altered $1 price and $11 amount.',
    'Price manipulation can create underpriced orders. No real payment or fraud was performed.',
    'Accept only product ID, variant and quantity; derive immutable line prices and discounts from server rules.',
    'Tampered prices are rejected or ignored and the stored price remains $200.', 'raw/api-validation.json', method='Authenticated API test')
add('Order endpoint trusts the submitted total amount','Order API','Security','High','/order/placeOrder',
    'Keep one valid line priced $200 with quantity 1. | Submit amount=1 rather than the displayed $210. | Fetch own orders.',
    'The server calculates the payable total from validated lines and shipping.',
    'The amount of 1 is persisted despite the unchanged $200 item.',
    'Totals can be manipulated independently of line-item prices.',
    'Recalculate all monetary values on the server with an explicit currency and rounding policy.',
    'Altered totals cannot be stored; valid item $200 plus $10 shipping yields $210.', 'raw/api-validation.json', method='Authenticated API test')
add('Cart endpoint stores a negative fractional quantity','Cart API','Data integrity','High','/cart/update',
    'Use only the demo account cart. | Update an item quantity to -0.5. | Fetch the cart and reload its page.',
    'Cart quantities remain positive integers; removal uses an explicit operation.',
    'The update succeeds and -0.5 persists. The invalid fixture produced a fractional badge and negative totals.',
    'Cart arithmetic and checkout readiness become invalid.',
    'Validate integer bounds server-side and sanitize existing invalid entries before computing totals.',
    'Invalid quantities fail and the cart remains unchanged; valid increments and removal still work.', 'raw/cart-validation.json;evidence/session-log.json', method='Authenticated API test', note='Only the invalid demo entries created for this test were subsequently removed.')
add('Cart endpoint accepts an unsupported size','Cart API','Data integrity','High','/cart/add',
    'Authenticate as the disposable account. | Add the valid product with size=QA-NOT-A-SIZE. | Fetch its cart.',
    'The server rejects a variant not listed for that product.',
    'The unsupported size is stored in cartData.',
    'The cart holds a selection the storefront cannot legitimately fulfil.',
    'Resolve the product variant before writing cart state and return a validation error for unknown sizes.',
    'Unsupported size is rejected with no cart change; valid size M is accepted.', 'raw/cart-validation.json', method='Authenticated API test', note='The test entry was removed after evidence capture.')
add('Cart endpoint accepts a non-existent product','Cart API','Data integrity','High','/cart/add',
    'Add ID 000000000000000000000000, size M to the demo cart. | Fetch the cart and reload it.',
    'The cart accepts only existing saleable products.',
    'The fabricated ID is stored but cannot be resolved into a visible valid product row.',
    'Hidden invalid entries create inconsistent cart state and can break order construction.',
    'Validate product existence on write and safely flag or remove stale references on read.',
    'Unknown IDs are rejected; deletion or unavailability of a previously valid product has a clear recovery state.', 'raw/cart-validation.json;evidence/session-log.json', method='Authenticated API test', note='The fabricated test entry was removed after capture.')
add('Guest checkout loses the address when authentication is required','Checkout','Functionality','Medium','/PlaceOrder',
    'As a guest with an item, complete the delivery form. | Press PLACE ORDER. | Follow the authentication flow.',
    'Authentication is requested before data entry, or the draft and checkout destination are preserved.',
    'Login is requested only on submission; the entered address is lost and successful signup returns to Home.',
    'A customer must repeat delivery entry and navigate back to checkout.',
    'Guard checkout earlier or preserve a draft and returnTo destination across authentication.',
    'Guest-to-login and guest-to-signup flows return to checkout with the valid draft and cart intact.', 'evidence/checkout-fields.json;evidence/signup-outcome.json;raw/app.js')
add('Postal field strips letters from an alphanumeric code','Checkout','Functionality','Medium','/PlaceOrder',
    'Type SW1A 1AA into Zipcode using normal keystrokes. | Read the resulting field value.',
    'A postal identifier is preserved for a supported destination; unsupported countries are explicitly excluded.',
    'The number input retains only 11 from SW1A 1AA. Country remains unrestricted free text.',
    'A legitimate alphanumeric postal code cannot be entered accurately.',
    'Use type=text, preserve spaces and letters, and validate against the supported-country policy.',
    'SW1A 1AA is preserved when the UK is supported; otherwise the UI clearly restricts destination selection.', 'evidence/checkout-form-limitations.json;evidence/checkout-form-limitations.jpg', note='Supported-country requirements were not supplied; unrestricted country entry makes the current constraint ambiguous.')
add('Phone field rejects a normally formatted telephone string','Checkout','Functionality','Medium','/PlaceOrder',
    'Type +1 (415) 555-0321 into Phone number. | Inspect the resulting value.',
    'A telephone string can be entered and normalized without corrupting its meaning.',
    'The type=number control does not retain the entered formatted phone; the recorded value is empty.',
    'Customers cannot paste a commonly formatted contact number.',
    'Use type=tel and appropriate inputmode, retaining the original string until validated and normalized.',
    'Formatted supported phone numbers work; invalid values receive a field-specific error.', 'evidence/checkout-form-limitations.json;evidence/checkout-form-limitations.jpg')
add('Unknown route has no not-found message or recovery','Routing','Functionality','Medium','/qa-route-does-not-exist',
    'Open the stated unknown URL. | Allow the application to settle.',
    'A not-found view explains the invalid route and links to a valid destination.',
    'Only the shared header and footer appear; the route receives the SPA HTML with HTTP 200.',
    'Broken links leave users in an unexplained page and are difficult to diagnose.',
    'Add a catch-all route with a clear message and recovery link; use an appropriate status when the hosting architecture permits.',
    'Unknown routes show Not found; known deep links still load on refresh.', 'evidence/unknown-route.json;evidence/unknown-route.jpg;raw/route-responses.json')
add('Profile response includes password and refresh-token fields','Account API','Security','High','/user/getUser',
    'Sign in only as the disposable account. | Inspect the field names returned by the own-profile endpoint.',
    'The response contains only client-required profile data and excludes authentication internals.',
    'The field list includes password and refreshToken, as well as internal persistence metadata. Secret values were not copied into this report.',
    'Authentication material is unnecessarily exposed to client code. This is not evidence of access to other users.',
    'Return an explicit safe profile DTO and exclude password hashes, refresh tokens and internal metadata from serialization.',
    'Own-profile and login responses omit these fields while authorised profile functions still work.', 'raw/api-validation.json', method='Authenticated API response inspection')

# Accessibility checks identify separate controls and their actual semantics.
add('Search opener cannot be activated with the keyboard','Shared layout','Accessibility','Medium','/',
    'Inspect the search icon. | Traverse the header with Tab and attempt keyboard activation.',
    'The search opener is a named keyboard-operable button.',
    'The clickable image has no button role or tabindex and is absent from the normal interactive sequence.',
    'Keyboard-only shoppers cannot open search.',
    'Use a button with an accessible name such as Open search, preserving the icon as decorative.',
    'Tab reaches the opener and Enter or Space opens the search form.', 'evidence/home-mobile.json;raw/app.js', method='DOM and public code review')
add('Search close icon lacks a keyboard action and name','Collection','Accessibility','Medium','/collection',
    'Open the search bar. | Inspect its close icon and try keyboard traversal.',
    'Close search is a named button reachable with Tab.',
    'The close affordance is a clickable image with empty alternative text and no button semantics.',
    'The visible closing action is unavailable to keyboard and screen-reader users.',
    'Wrap the icon in a button labelled Close search and restore focus to the opener when it closes.',
    'The action is announced by name and closes the bar with Enter or Space.', 'evidence/search-no-results.json;raw/app.js', method='DOM and public code review')
add('Authenticated account menu is not keyboard operable','Account','Accessibility','Medium','/',
    'Sign in and inspect the profile opener. | Inspect Orders and Logout in its menu.',
    'The opener and menu actions have suitable keyboard behaviour and semantic roles.',
    'The opener is a clickable div and image; menu actions are clickable paragraphs without normal keyboard semantics.',
    'Keyboard users cannot reliably open or use the account menu, including logout.',
    'Use a named disclosure button, a link for Orders and a button for Logout with proper focus handling.',
    'The entire account menu can be opened, traversed, activated and dismissed using the keyboard.', 'evidence/profile-no-action.json;raw/app.js', method='DOM and public code review')
add('Login and Create Account mode switch is not a keyboard control','Account','Accessibility','Medium','/login',
    'Open the account form. | Inspect and attempt keyboard activation of Login or Create Account.',
    'The mode switch is an operable button or link.',
    'The switch is a paragraph with an onClick handler and no keyboard control semantics.',
    'Keyboard users cannot select the alternative authentication form.',
    'Use a type=button mode switch or links to explicit account routes.',
    'Enter and Space switch modes without submitting the form accidentally.', 'evidence/login-form.json;raw/app.js', method='DOM and public code review')
add('Product gallery thumbnails are pointer-only controls','Product','Accessibility','Medium',PRODUCT,
    'Open the product with multiple gallery images. | Inspect the thumbnail controls.',
    'Each thumbnail is keyboard operable and identifies the image it selects.',
    'Thumbnails are clickable images without button roles or tabindex.',
    'Keyboard shoppers cannot inspect alternative product views.',
    'Use named buttons around thumbnails, exposing selected state and a visible focus indicator.',
    'All images can be selected using Tab and Enter; selected image state is announced.', 'evidence/product-details.json;raw/app.js', method='DOM and public code review')
add('Remove cart item is an unnamed pointer-only image','Cart','Accessibility','Medium','/cart',
    'Add one valid item. | Inspect the bin icon used to remove the row.',
    'Removal is a named keyboard-operable button identifying its item.',
    'The bin is an image click target without suitable alternative text or button semantics.',
    'Keyboard and assistive-technology users cannot reliably remove a line item.',
    'Use a button labelled Remove [product name] with a clear focus style.',
    'The item is removable with the keyboard and focus moves to a sensible remaining control.', 'evidence/cart-one-item.json;raw/app.js', method='DOM and public code review')
add('Cart product navigation is available only through a clickable image','Cart','Accessibility','Medium','/cart',
    'Add one item. | Inspect its image-based route to the product.',
    'An ordinary product link is available and identifies the destination.',
    'The image uses a click handler rather than an anchor; the visible product name is also blank.',
    'Keyboard users cannot use the cart shortcut back to product details.',
    'Use an anchor containing an informative product name or image alternative.',
    'Tab reaches a named product link and Enter opens the correct product.', 'evidence/cart-one-item.json;raw/app.js', method='DOM and public code review')
add('Mobile menu opener has no button semantics','Shared layout','Accessibility','Medium','/',
    'Use a 390 px viewport. | Inspect the menu icon.',
    'Open menu is a named button with its expanded state exposed.',
    'The visible opener is a clickable image without button semantics or aria-expanded.',
    'Keyboard and assistive-technology users cannot reliably open mobile navigation.',
    'Use a button with aria-expanded and aria-controls tied to the menu panel.',
    'Keyboard activation opens the menu and the announced state changes.', 'evidence/home-mobile.json;evidence/mobile-menu-open.json;raw/app.js', method='Responsive DOM review')
add('Mobile menu Back affordance is not keyboard operable','Shared layout','Accessibility','Medium','/',
    'Open mobile navigation. | Inspect its Back image and text.',
    'The visible closing control is a keyboard-operable, named button.',
    'Back is implemented with a clickable div, image and paragraph rather than a button.',
    'A keyboard user lacks a reliable explicit close control.',
    'Use a Close menu button and return focus to the original opener.',
    'Tab reaches Close menu; Enter or Space closes the panel and restores focus.', 'evidence/mobile-menu-open.json;raw/app.js', method='Responsive DOM review')
add('Closed mobile menu leaves offscreen links in the accessibility tree','Shared layout','Accessibility','Medium','/',
    'At mobile width, close the menu. | Inspect the menu links and their hiding mechanism.',
    'Collapsed navigation content is removed from interactive and accessibility navigation.',
    'The panel is moved with translate-x-full; its links remain in the snapshot and are not inert or aria-hidden.',
    'Assistive navigation can expose offscreen destinations unrelated to the visible interface.',
    'Conditionally mount the closed panel or use an appropriate inert/hidden state, restoring it when opened.',
    'Closed links are absent from the accessibility and tab sequence; opening makes them available.', 'evidence/home-mobile.json;raw/app.js', method='Responsive DOM and code review', note='The observed accessibility-tree exposure is confirmed; individual assistive-technology behaviour was not separately tested.')
add('Mobile menu does not manage focus or dismiss on Escape','Shared layout','Accessibility','Medium','/',
    'Open the mobile menu. | Press Escape while a navigation item is focused. | Inspect focus handling.',
    'An overlay menu provides predictable focus and dismissal behaviour.',
    'Escape leaves the menu open; no opening focus transfer or closing focus restoration is implemented.',
    'Keyboard users can lose their position in navigation.',
    'Choose a disclosure or dialog interaction model and implement its focus and Escape behaviour consistently.',
    'Open, traverse, Escape and reopen the menu; focus remains predictable throughout.', 'evidence/mobile-menu-escape.json;evidence/mobile-menu-open.json;raw/app.js')
add('Mobile filter disclosure is a paragraph rather than a control','Collection','Accessibility','Medium','/collection',
    'Use mobile Collection. | Inspect the FILTERS toggle.',
    'A button opens filters and exposes expanded or collapsed state.',
    'The toggle is a clickable paragraph without button semantics or expanded-state metadata.',
    'Keyboard and assistive users cannot reliably discover and operate filtering.',
    'Use a button with aria-expanded and aria-controls for the filter group.',
    'Keyboard opening works and the state is announced correctly.', 'evidence/mobile-filters-open.json;raw/app.js', method='Responsive DOM review')
add('Payment methods are not keyboard selectable radio controls','Checkout','Accessibility','Medium','/PlaceOrder',
    'Open checkout. | Traverse to the Stripe and Cash on Delivery choices.',
    'Payment methods form a labelled radio group with keyboard selection and selected-state exposure.',
    'The choices are clickable divs and decorative circles, with no radio or button semantics.',
    'Keyboard customers cannot select a payment method reliably.',
    'Use labelled radio inputs in a fieldset and expose the selected payment option.',
    'Tab and arrow keys select each method; the selected method is announced.', 'evidence/checkout-form-limitations.json;raw/app.js', method='DOM and public code review')
add('Stripe option has no accessible payment-provider name','Checkout','Accessibility','Medium','/PlaceOrder',
    'Inspect the Stripe choice in the checkout accessibility snapshot.',
    'The provider name Stripe is available as text or an accessible label.',
    'Only a logo with alt="" appears; the option has no text label and is absent as a named choice.',
    'A screen-reader user cannot identify this visible payment option.',
    'Add the text label Stripe to its radio option; retain the logo as decorative.',
    'The provider is announced as Stripe together with its selected state.', 'evidence/checkout-form-limitations.json;evidence/checkout-form-limitations.jpg', method='DOM review', note='This checks the accessible name, separately from the keyboard-selection defect.')
add('Selected product size is communicated only by colour','Product','Accessibility','Medium',PRODUCT,
    'Select size M. | Inspect its button attributes before and after selection.',
    'The selected variant has a programmatically exposed state.',
    'Only the border/background classes change; no aria-pressed or radio checked state indicates the selected size.',
    'Assistive users cannot determine which size will be added.',
    'Use a labelled size radio group, or expose aria-pressed consistently on selection buttons.',
    'Selecting M announces its state and clears the previous selection.', 'evidence/related-size-carryover.json;raw/app.js', method='DOM and public code review')
add('Collection sort selector has no associated label','Collection','Accessibility','Medium','/collection',
    'Inspect the sort select element and its labels or aria-label.',
    'The control has a programmatic label explaining its purpose.',
    'The select has no label, id association or aria-label; only option text contains Sort by.',
    'The control purpose depends on selected option text rather than a stable accessible name.',
    'Associate a Sort products label with the select.',
    'The control is announced by its purpose with each available option.', 'evidence/collection-loaded.jpg;raw/app.js', method='DOM and code review')
add('Delivery fields rely on disappearing placeholders','Checkout','Accessibility','Medium','/PlaceOrder',
    'Inspect delivery inputs before entry. | Type values into first name, address and contact fields.',
    'Persistent visible labels identify the fields after entry and provide programmatic associations.',
    'There are no associated labels; placeholders disappear as values are entered. Numeric postal and phone controls appear unnamed in the snapshot.',
    'Customers lose field context and assistive users encounter unnamed controls.',
    'Add label elements linked to stable input IDs for every delivery field; keep placeholders as optional examples.',
    'All nine fields retain visible and accessible names after entry.', 'evidence/checkout-fields.json;evidence/checkout-form-limitations.json')
add('Authentication fields have no persistent associated labels','Account','Accessibility','Medium','/login',
    'Open Signup or Login. | Fill username, email and password and inspect labels.',
    'Each credential field retains a visible label and programmatic association.',
    'Only placeholders identify the fields; no label associations are present.',
    'Entered forms lose clear visual context and depend on placeholder interpretation.',
    'Add associated Username, Email and Password labels to the account form.',
    'Both modes keep field names visible and expose them correctly after entry.', 'evidence/login-form.json;raw/app.js', method='DOM and public code review')
add('Personal-data inputs do not expose their autocomplete purposes','Checkout','Accessibility','Medium','/PlaceOrder',
    'Inspect autocomplete attributes on delivery name, address, email and phone inputs.',
    'Known personal-data purposes are exposed using appropriate autocomplete tokens.',
    'The fields do not specify purpose tokens such as given-name, street-address, postal-code or tel.',
    'Assistive personalization and reliable browser autofill lack explicit field-purpose metadata.',
    'Add correct autocomplete tokens for each supported personal-data field and authentication mode.',
    'Inspect the corrected DOM and verify a test autofill preserves each field purpose.', 'evidence/checkout-form-limitations.json;evidence/login-form.json', method='DOM review')
add('Muted home-page text has insufficient contrast','Home','Accessibility','Medium','/',
    'Inspect policy and newsletter text rendered in gray-400 on white. | Calculate contrast from the observed computed colour.',
    'Normal-size text meets a minimum 4.5:1 contrast ratio.',
    'The computed colour is oklch(0.707 0.022 261.325) at 16 px on white; the calculated ratio is below 4.5:1.',
    'Low-vision users may struggle to read service-policy and newsletter text.',
    'Use a darker approved text colour and check all states against the real background.',
    'The same text at 16 px measures at least 4.5:1 without relying on rounding.', 'evidence/typography-semantics.json', method='Computed-style measurement', note='The exact converted sRGB colour and ratio are included in the evidence summary.')
add('Newsletter input suppresses its visible keyboard focus','Home','Accessibility','Medium','/',
    'Focus SUBSCRIBE, then Shift+Tab into the email input. | Inspect the focus outline and screenshot.',
    'Keyboard focus is visibly indicated on the input.',
    'The input uses outline-none and no focus shadow; the observed focus has no visible outline or replacement.',
    'Keyboard users cannot easily locate the active subscription field.',
    'Provide a distinct focus-visible border or outline with sufficient contrast.',
    'Tab and Shift+Tab clearly indicate focus without requiring pointer interaction.', 'evidence/newsletter-focus.jpg;raw/app.js', method='Keyboard test and style review')
add('Meaningful product photographs have empty alternative text','Product','Accessibility','Medium',PRODUCT,
    'Inspect the main product image and gallery alternatives.',
    'Meaningful product views have concise text alternatives describing the item or view.',
    'The product images use alt="" despite conveying garment identity and appearance.',
    'Screen-reader users cannot obtain information conveyed by the product photography.',
    'Provide accurate item and view alternatives; use empty alt only for genuinely decorative or fully redundant images.',
    'The main image and each informative gallery view expose useful, non-duplicative alternatives.', 'evidence/product-details.json;raw/app.js', method='DOM review')
add('Visible page and section titles are not semantic headings','Shared layout','Accessibility','Medium','/collection',
    'Inspect Collection, Cart, Checkout, About and Contact heading outlines.',
    'Page titles and major sections use a logical h1-h2 hierarchy.',
    'The inspected pages have paragraph-based titles and no h1-h3 outline; the common title component renders a p.',
    'Assistive heading navigation cannot follow the visible document structure.',
    'Use semantic headings in the shared title component with context-appropriate levels.',
    'Every page has a meaningful h1 and logical section headings without skipped structural levels.', 'evidence/collection-reload.json;evidence/about-page.json;evidence/contact-page.json;raw/app.js', method='DOM review')
add('Page content lacks main and footer landmarks','Shared layout','Accessibility','Low','/',
    'Inspect document landmarks on Home and Collection.',
    'Main content and the site footer have suitable landmark semantics.',
    'No main or contentinfo/footer landmarks are present; major regions are generic containers.',
    'Assistive users have fewer efficient ways to navigate page regions.',
    'Use one main element per page and a footer for shared closing content.',
    'Landmark navigation identifies Navigation, Main and Content information in a sensible order.', 'evidence/typography-semantics.json', method='DOM review')
add('Browser title does not identify the current page','Shared layout','Accessibility','Low','/collection',
    'Navigate between Home, Collection, Product, About and Checkout. | Compare document.title.',
    'Each title describes its page purpose and the store.',
    'All inspected routes retain Forever Mart.',
    'Tabs and assistive page announcements do not distinguish destinations.',
    'Set route-specific titles such as Collection | ForeverMart and include product names on detail pages.',
    'Each route and direct deep link exposes an accurate title.', 'evidence/collection-reload.json;evidence/product-details.json;evidence/about-page.json;evidence/checkout-fields.json')
add('Layout overflows horizontally at 320 CSS pixels','Shared layout','Accessibility','Medium','/PlaceOrder',
    'Set the viewport to 320 CSS px. | Inspect the header and checkout document width.',
    'The page reflows without horizontal scrolling for ordinary content.',
    'Measured widths exceeded the viewport: header state 343 px and checkout 352 px. Checkout includes a min-w-80 total panel within page margins.',
    'Small-screen and zoomed users must pan horizontally to reach content.',
    'Remove fixed minimum widths that exceed the available content area; wrap header controls and stacked form panels.',
    'At 320 CSS px, document width is no greater than the viewport and all controls remain usable.', 'evidence/checkout-320-dimensions.json;raw/app.js', method='Responsive measurement', note='A screenshot at this viewport could not be captured by the browser tool; the dimension measurement is preserved.')

# Content defects and clearly marked quality observations
add('Home-page hero misspells Arrivals','Home','Content','Low','/',
    'Open Home and read the hero heading.', 'The heading reads Latest Arrivals.', 'The visible heading reads Latest Arivals.',
    'The first impression contains a spelling mistake.', 'Correct the copy and add a content proofreading checklist.',
    'The rendered heading and accessible heading text both read Latest Arrivals.', 'evidence/home-desktop.jpg;raw/app.js')
add('Template filler text remains in customer-facing sections','Shared layout','Content','Low','/',
    'Read the home collection descriptions, newsletter copy and footer.', 'Public copy explains the store and each section.',
    'Several visible paragraphs contain Lorem ipsum template text.', 'Customers see unfinished content instead of useful information.',
    'Replace all placeholder paragraphs with approved store copy and search the production content for template text.',
    'No Lorem ipsum remains on public routes; reviewed copy is meaningful.', 'evidence/home-desktop.jpg;evidence/about-page.json;raw/app.js')
add('Contact details conflict between the footer and Contact page','Contact','Content','Medium','/contact',
    'Compare Contact page details with its footer.', 'The store publishes one verified contact set, or clearly labels different departments.',
    'The footer shows +1-212-444-780 and contact@foreveryou.com; Contact shows (415) 555-0321 and admin@forever.com without an explanation.',
    'Customers do not know which contact details belong to the store.', 'Centralize approved contact data and label any distinct support or administrative contacts.',
    'Each route shows the same approved support contact or explains the difference.', 'evidence/contact-page.json;evidence/contact-page.jpg')
add('About page contains an incomplete support sentence','About','Content','Low','/about',
    'Read the support paragraph on About.', 'The sentence is complete and understandable.',
    'The copy ends with assist you the way, leaving the intended meaning incomplete.', 'The About page communicates unfinished copy.',
    'Rewrite the sentence and proofread the complete About page.', 'The paragraph is grammatically complete and approved by the content owner.', 'evidence/about-page.json')
add('Winterwear filter has no matching catalogue classification','Collection','Usability','Low','/collection',
    'Select winterwear and compare the public subCategory values.', 'Filter options reflect available classifications or explain an empty category.',
    'winterwear returns an empty grid; the catalogue uses only Topwear and Bottomwear, including for jackets.', 'An apparently useful filter has no compatible records.',
    'Align the taxonomy and product classification, or omit unavailable options until they contain products.',
    'Every advertised filter is backed by the intended classification or has an explicit empty state.', 'evidence/winterwear-filter.json;raw/products.json', classification='Observation', note='The intended garment taxonomy requires owner confirmation.')
add('Empty cart has no explanatory state or shopping recovery','Cart','Usability','Low','/cart',
    'Open the cart with zero items.', 'The page states that the cart is empty and offers a clear shopping action.',
    'There are no rows or empty-cart explanation, but checkout remains the main action.', 'Customers receive little guidance when nothing is selected.',
    'Add an empty-cart message and a Continue shopping link; suppress checkout in that state.',
    'A new or cleared cart has a clear recovery action.', 'evidence/cart-empty.json;evidence/cart-empty.jpg', classification='Observation')
add('Checkout does not show the products being purchased','Checkout','Usability','Medium','/PlaceOrder',
    'Open checkout after adding a valid item. | Inspect the review information.', 'A shopper can verify product, variant and quantity before submission.',
    'Only monetary totals and address fields are shown; no item summary is presented.', 'The final screen does not help customers catch selection mistakes.',
    'Include a concise order summary with item names, quantities, sizes and prices, with an edit-cart link.',
    'The summary agrees with the cart and server-calculated final order.', 'evidence/checkout-fields.json;evidence/checkout-fields.jpg', classification='Observation')
add('Order history omits order identifiers','Orders','Usability','Medium','/order',
    'Open own demo order history and compare it with the own-orders API.', 'Customers have a visible order reference for support.',
    'The API has order IDs, but the interface does not display them.', 'A customer cannot cite an unambiguous order reference from the interface.',
    'Show a safe order reference on each order group and use it in support or detail links.',
    'Each displayed order has a unique visible reference matching its record.', 'evidence/orders-validation-tests.json;raw/api-validation.json', classification='Observation')
add('Order history loses order-level grouping','Orders','Usability','Medium','/order',
    'Inspect the own order history and the public order-view component.', 'Line items are grouped under the order that owns them.',
    'The component pushes all order items into one list and renders item rows without order containers.', 'Customers cannot clearly distinguish separate purchases with similar items.',
    'Render order-level sections containing their line items, reference, date and total.',
    'Two orders and a multi-item order are visually distinguishable; empty invalid records are not silently hidden.', 'evidence/orders-validation-tests.json;raw/app.js', classification='Observation', method='Browser and public code review', note='The flattening implementation was inspected; a multi-item-order scenario was not executed.')
add('Order history omits the final order total and shipping breakdown','Orders','Usability','Medium','/order',
    'Inspect the order priced $210 in the own-orders data and its visible row.', 'The customer can verify the stored final payable amount.',
    'Only item price and quantity are shown; the stored order total and shipping breakdown are not displayed.', 'The view cannot serve as a complete order cost confirmation.',
    'Show order subtotal, shipping, discounts where applicable, currency and final total from the validated order record.',
    'The $200 test item plus $10 shipping displays a $210 final total.', 'evidence/orders-validation-tests.json;raw/api-validation.json', classification='Observation')
add('Order history has no delivery-address review','Orders','Usability','Low','/order',
    'Open own order history after the test order. | Inspect the delivery information available to the customer.',
    'An order detail view allows the customer to review the submitted delivery address safely.',
    'The visible history provides no address or detail link for reviewing it.', 'A delivery-entry mistake cannot be checked from the current customer interface.',
    'Provide an authenticated order-detail view with the delivery address and contact information.',
    'Own order details show the stored address; another account cannot retrieve it.', 'evidence/orders-validation-tests.json;raw/demo-orders.json', classification='Observation')
add('About page advertises product ranges absent from the inspected catalogue','About','Content','Low','/about',
    'Read the advertised product ranges. | Compare with the 40 returned product records.',
    'Marketing copy reflects the current offer or explicitly describes future ranges.',
    'About mentions electronics, beauty and home essentials while the inspected catalogue contains apparel only.',
    'The current copy can create expectations the store does not presently meet.',
    'Align copy with the current catalogue or label future expansion clearly.',
    'Each current-range claim is supported by published products.', 'evidence/about-page.json;raw/products.json', classification='Observation')
add('Newsletter placeholder contains incorrect wording','Home','Content','Low','/',
    'Inspect the newsletter email placeholder.', 'The field instruction is clear and correctly written.',
    'The placeholder reads enter you email.', 'A visible entry instruction contains a grammar error.',
    'Use a persistent Email address label and an optional example placeholder.',
    'The form contains clear approved wording before and after entry.', 'evidence/home-mobile.json')
add('Copyright footer contains incomplete grammar and inconsistent branding','Shared layout','Content','Low','/',
    'Read the copyright footer and compare its named domain with the store identity.',
    'The notice is correctly written and uses the approved store or legal-owner identity.',
    'The line reads Copyright 2025@ forever.com -All Right Reserved.; the store is presented as Forever Mart.',
    'The footer appears unfinished and its ownership identity needs clarification.',
    'Use the approved legal identity and All rights reserved wording. Verify the year policy rather than automatically replacing it.',
    'The notice is grammatically correct and its owner is approved.', 'evidence/home-mobile.json', classification='Observation', note='A 2025 year is not itself classified as a defect; it may identify the original publication year.')
add('Public document has no Content Security Policy','Platform','Security','Medium','/',
    'Inspect the saved response headers and public HTML head.',
    'A production hardening policy limits script and other resource sources as appropriate to this app.',
    'Neither a Content-Security-Policy response header nor a CSP meta policy is present in the inspected document.',
    'The page lacks this defence-in-depth control; no script-injection exploit was demonstrated.',
    'Develop a least-privilege CSP using report-only validation before enforcing it, including the actual API, image and payment dependencies.',
    'The reviewed policy is present and all authorised app flows work without unexpected violations.', 'raw/headers.json;raw/home.html', classification='Observation', method='HTTP configuration review')
add('Public document lacks an explicit framing restriction','Platform','Security','Medium','/',
    'Inspect frame-related response headers and policy directives.',
    'The deployment restricts embedding to explicitly approved origins.',
    'No X-Frame-Options or CSP frame-ancestors restriction is present in the inspected response.',
    'Clickjacking defence is not configured in this response; an exploit was not attempted.',
    'Set a suitable CSP frame-ancestors policy and, where appropriate, X-Frame-Options for older clients.',
    'An unauthorised framing origin is blocked and approved integrations continue to work.', 'raw/headers.json', classification='Observation', method='HTTP configuration review')
add('Public responses omit the nosniff hardening header','Platform','Security','Low','/',
    'Inspect X-Content-Type-Options in the saved public response.',
    'Responses use correct content types and X-Content-Type-Options: nosniff.',
    'The inspected response contains no X-Content-Type-Options header.',
    'An additional browser MIME-sniffing defence is absent; no MIME-confusion exploit was demonstrated.',
    'Configure nosniff consistently and verify asset MIME types.',
    'HTML, script, stylesheet and image responses have correct types and the intended header.', 'raw/headers.json', classification='Observation', method='HTTP configuration review')
add('Public document has no explicit Referrer Policy','Platform','Security','Low','/',
    'Inspect Referrer-Policy headers and meta tags in the document.',
    'The application explicitly defines the referrer information it permits external destinations to receive.',
    'No explicit policy is present; browser defaults determine behaviour.',
    'The deployment leaves this privacy setting implicit; this finding does not claim a proven data leak.',
    'Choose and configure an appropriate policy such as strict-origin-when-cross-origin after reviewing navigation needs.',
    'Inspect same-origin and cross-origin navigation to confirm the intended information is sent.', 'raw/headers.json;raw/home.html', classification='Observation', method='HTTP configuration review')
add('Offscreen catalogue images are not marked for lazy loading','Collection','Performance','Low','/collection',
    'Load the 40-product collection. | Inspect loading attributes on product images below the fold.',
    'Non-critical offscreen images can defer loading while initial visible content remains prioritised.',
    'The inspected image elements have no loading=lazy attribute.',
    'The implementation misses a possible transfer-saving optimisation; no Core Web Vitals failure is claimed.',
    'Lazy-load offscreen cards, keep initial visible images eager, and measure the impact on a representative device.',
    'A network trace verifies deferred offscreen requests without delaying visible products.', 'evidence/collection-reload.json;evidence/typography-semantics.json;raw/app.js', classification='Observation', method='DOM and code review')
add('Product images do not advertise responsive source variants','Collection','Performance','Low','/collection',
    'Inspect catalogue image srcset and sizes attributes at desktop and mobile widths.',
    'Image delivery can select a suitably sized source for the rendered card.',
    'The inspected images use a single source with no srcset or sizes attributes.',
    'Smaller screens cannot request a deliberately smaller variant through these attributes; actual speed impact was not measured.',
    'Generate appropriate Cloudinary or equivalent variants and declare sizes and srcset.',
    'Mobile and desktop request suitable image dimensions while retaining image quality.', 'evidence/typography-semantics.json;evidence/collection-mobile.json', classification='Observation', method='DOM review')
add('Public pages lack a page-specific meta description','Routing','Discoverability','Low','/collection',
    'Inspect the document head and route title updates.',
    'Indexable store pages provide concise, page-specific descriptive metadata.',
    'The inspected HTML has no meta description and the client does not populate a route-specific description.',
    'Search and sharing systems have little authored summary information. This is an optimisation observation.',
    'Add approved descriptions for indexable routes and product pages using a route-aware metadata strategy.',
    'Rendered page heads contain distinct relevant descriptions without indexing private account routes.', 'raw/home.html;evidence/typography-semantics.json;raw/app.js', classification='Observation', method='HTML and code review')
add('Footer email and telephone cannot be activated directly','Contact','Usability','Low','/contact',
    'Inspect and click the email and telephone strings in the footer and contact details.',
    'Customers can activate an approved support email or phone link on compatible devices.',
    'The details are static text without mailto or tel links.',
    'Customers must manually copy contact information, especially awkward on phones.',
    'After approving the contact values, provide mailto and tel links with meaningful accessible names.',
    'The links invoke the corresponding device action without sending a message automatically.', 'evidence/contact-page.json;raw/app.js', classification='Observation')
add('Checkout does not state which dollar currency is used','Checkout','Usability','Low','/PlaceOrder',
    'Inspect the displayed prices and final checkout total.',
    'The payable amount identifies its currency unambiguously.',
    'Only $ is shown; no ISO currency label is displayed while the country field is unrestricted.',
    'An international customer cannot distinguish USD from other dollar currencies from the checkout display.',
    'Display the actual supported ISO currency next to the final total and align the payment configuration.',
    'Cart, checkout and order confirmation use one consistent, explicit currency.', 'evidence/checkout-fields.json;raw/app.js', classification='Observation')
add('Displayed return and exchange promises lack instructions','Home','Usability','Low','/',
    'Read Easy Exchange Policy and 7 Days Return Policy. | Look for a working route to the policy details.',
    'Customers can read the scope, conditions and procedure behind these service promises.',
    'The promises are brief text only; the inspected interface provides no usable policy-detail route or procedure.',
    'Customers cannot determine how to request the promised service.',
    'Publish owner-approved policy details and link directly from the service summary.',
    'A customer can find eligibility, timeframe, procedure and support contact from each summary.', 'evidence/home-mobile.json;raw/app.js', classification='Observation')

def build():
    assert len(records) == 90, f'Expected 90 distinct records, got {len(records)}'
    OUT.mkdir(parents=True, exist_ok=True)
    # Convert the observed OKLCH colour to linear sRGB for WCAG relative luminance.
    L,C,h = .707,.022,math.radians(261.325)
    a,b=C*math.cos(h),C*math.sin(h)
    l=(L+.3963377774*a+.2158037573*b)**3
    m=(L-.1055613458*a-.0638541728*b)**3
    s=(L-.0894841775*a-1.291485548*b)**3
    rgb=(4.0767416621*l-3.3077115913*m+.2309699292*s,
         -1.2684380046*l+2.6097574011*m-.3413193965*s,
         -.0041960863*l-.7034186147*m+1.707614701*s)
    luminance=.2126*rgb[0]+.7152*rgb[1]+.0722*rgb[2]
    contrast=1.05/(luminance+.05)
    encode=lambda c:12.92*c if c<=.0031308 else 1.055*c**(1/2.4)-.055
    srgb=[round(255*encode(c)) for c in rgb]
    measurement=dict(observed_colour='oklch(0.707 0.022 261.325)',background='white',
                     font_size_css_px=16,srgb_rounded=srgb,contrast_ratio=contrast,threshold=4.5,
                     method='OKLCH to linear sRGB; WCAG relative-luminance contrast against white')
    (OUT/'evidence/contrast-measurement.json').write_text(json.dumps(measurement,indent=2),encoding='utf-8')
    r=records[59]
    r['actual']=f'The computed colour is oklch(0.707 0.022 261.325) at 16 px on white, approximately RGB {srgb}. The calculated contrast ratio is {contrast:.2f}:1, below 4.5:1.'
    r['evidence'].append('evidence/contrast-measurement.json')
    records[65]['actual']='At 320 CSS px, the settled checkout document and body are both 352 px wide. The totals panel uses min-w-80 within the page margins.'
    records[65]['evidence']=['evidence/checkout-320-verified.json','evidence/checkout-320-verified.jpg','raw/app.js']
    records[65]['note']='Reproduced again at the stated viewport; a screenshot and the full DOM snapshot are retained.'
    for r in records:
        for e in r['evidence']:
            if not (OUT / e).exists():
                raise FileNotFoundError(f"{r['id']} references missing evidence {e}")
    (OUT / 'defect-registry.json').write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding='utf-8')
    fields=list(records[0])
    with (OUT/'defect-registry.csv').open('w', newline='', encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        writer.writerows({k:' | '.join(v) if isinstance(v,list) else v for k,v in r.items()} for r in records)
    summary={k:dict(Counter(r[k] for r in records)) for k in ('classification','severity','category','module','status')}
    summary['target']=100
    summary['findings']=len(records)
    summary['build_asset']='index-r3xEth_L.js'
    summary['bundle_sha256']=hashlib.sha256((OUT/'raw/app.js').read_bytes()).hexdigest()
    (OUT/'audit-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    build()
