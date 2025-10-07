# Book-Stay

latest version we reach

admin user type >> nada@gmail.com >> nada123456 (superuser)

Hotel-Owner user type >> mzughbor@gmail.com >> mahmoud123


-----------

latest reach to edit the related templeting about hotels and rooms by nada

mahmoud edit the login pages and registration front and back done

according to latest notice -- pages with number 1 is done


## Recent Updates (Oct 2025)

- Owner area expanded with three pages using a unified layout:
  - Dashboard (`/users/owner/dashboard/`): Overview stats, latest hotels, and a calendar section.
  - View my Hotels (`/users/owner/hotels/`): Two-card grid listing owner hotels with quick actions.
  - Profile (`/users/owner/profile/`): Editable account fields (name, username, email, phone, DOB, nationality, bio) with Save.

- Styling & Structure
  - Introduced `static/assets/css/owner-hotels.css` for page-scoped styles that match the site's theme.
  - Reused `owner-dashboard.css` for consistent sidebar/content layout.
  - Normalized buttons inside `.main-button` to ensure consistent appearance (anchors and buttons).
  - Mobile enhancements: added small top margin to `.od-content` on narrow screens.

- Hotels/Rooms Grids
  - Added `templates/hotels/all-rooms.html` for All Rooms view (3-column grid style).
  - Kept `hotels/all/` and `hotels/rooms/` routes for quick navigation.

- Authentication & Navigation
  - Login-only page at `/users/auth/` with links to customer and owner registration.
  - Owner sidebar links wired to Profile and View my Hotels.

- Calendar Integration (Owner Dashboard)
  - Replaced static preview with FullCalendar.
  - New JSON endpoint: `/users/owner/bookings-calendar-data/` serving color-coded events by daily reservation counts.
  - Frontend loads events dynamically and displays per-day totals with colors (green/yellow/red by load).

### How to Test Quickly

1. Start server:
   - `python3 manage.py runserver`
2. Log in as an owner (example user in this README) and open:
   - Dashboard: `/users/owner/dashboard/`
   - My Hotels: `/users/owner/hotels/`
   - Profile: `/users/owner/profile/`
3. Verify buttons, card styles, and calendar events load.

### Notes

- The calendar data endpoint currently returns mocked counts; replace with real aggregation from bookings when ready.
- New CSS is scoped to owner pages to avoid affecting the rest of the site.

