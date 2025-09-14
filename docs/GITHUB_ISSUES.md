# 📋 GitHub Issues to Create

Copy and create these issues on GitHub: https://github.com/veacheslavv/telegram-gym-bot/issues

## High Priority Issues

### Issue #1: Implement Data Export Functionality
**Title**: Implement Data Export Functionality (Excel, PDF, CSV)
**Labels**: enhancement, high-priority, backend
**Description**:
```
## Description
Add data export functionality to allow users to export their workout data in various formats.

## Tasks
- [ ] Implement Excel export using openpyxl
- [ ] Implement PDF generation using reportlab
- [ ] Implement CSV export
- [ ] Add /export command handler
- [ ] Create export format selection menu
- [ ] Add email delivery option

## Acceptance Criteria
- Users can export last 30 days of workouts
- Export includes all workout details
- Files are properly formatted
```

### Issue #2: Complete Progress Charts and Visualizations
**Title**: Add Progress Charts and Data Visualizations
**Labels**: enhancement, high-priority, feature
**Description**:
```
## Description
Implement visual progress tracking with charts and graphs.

## Tasks
- [ ] Fix matplotlib async rendering
- [ ] Create volume progression charts
- [ ] Add strength progress graphs
- [ ] Implement muscle group distribution pie chart
- [ ] Create workout frequency heatmap
- [ ] Add /progress command handler

## Technical Requirements
- Use matplotlib/seaborn for charts
- Save charts as images for Telegram
- Cache generated charts
```

### Issue #3: Complete Personal Records System
**Title**: Finish Personal Records (PR) Tracking System
**Labels**: enhancement, high-priority, feature
**Description**:
```
## Description
Complete the PR tracking system with automatic detection and notifications.

## Tasks
- [ ] Implement automatic PR detection algorithm
- [ ] Add PR notification system
- [ ] Create /records command with full UI
- [ ] Add PR history view
- [ ] Implement PR categories (1RM, volume, reps)

## Features
- Auto-detect new PRs during workout logging
- Send celebration message for new PRs
- Track PR history with dates
```

### Issue #4: Add Routine Creation UI
**Title**: Implement Routine Creation and Management UI
**Labels**: enhancement, high-priority, frontend
**Description**:
```
## Description
Create user interface for workout routine management.

## Tasks
- [ ] Add /create_routine command
- [ ] Implement routine builder conversation flow
- [ ] Add routine templates (PPL, Upper/Lower, etc.)
- [ ] Create routine following system
- [ ] Add progress tracking per routine

## User Flow
1. User selects /create_routine
2. Name the routine
3. Add exercises with target sets/reps
4. Save and activate routine
```

## Medium Priority Issues

### Issue #5: Expand Exercise Database
**Title**: Add More Exercises to Database
**Labels**: enhancement, medium-priority, data
**Description**:
```
## Description
Expand exercise database from 39 to 100+ exercises.

## Tasks
- [ ] Add more exercise variations
- [ ] Include bodyweight exercises
- [ ] Add cardio exercises
- [ ] Include stretching exercises
- [ ] Add exercise instructions and tips

## Categories to Expand
- Chest: Add flyes, pullovers
- Back: Add shrugs, good mornings
- Legs: Add Bulgarian split squats, hip thrusts
- Core: Add side planks, mountain climbers
```

### Issue #6: Implement Workout Templates
**Title**: Add Workout Template System
**Labels**: enhancement, medium-priority, feature
**Description**:
```
## Description
Allow users to save and reuse workout templates.

## Tasks
- [ ] Create template model
- [ ] Add save workout as template option
- [ ] Implement template library
- [ ] Add quick-log from template
- [ ] Share templates between users

## Benefits
- Faster workout logging
- Consistency in training
- Share popular workouts
```

### Issue #7: Add Body Measurements Tracking
**Title**: Implement Body Measurements Feature
**Labels**: enhancement, medium-priority, feature
**Description**:
```
## Description
Track body measurements and composition.

## Tasks
- [ ] Add measurement models
- [ ] Create /measurements command
- [ ] Track weight, body fat %, measurements
- [ ] Show measurement progress charts
- [ ] Add photo progress option

## Measurements
- Weight
- Body fat percentage
- Chest, arms, waist, thighs
- Progress photos
```

## Low Priority Issues

### Issue #8: Social Features Implementation
**Title**: Add Social Features (Friends, Sharing, Leaderboards)
**Labels**: enhancement, low-priority, feature
**Description**:
```
## Description
Implement social features for community engagement.

## Tasks
- [ ] Friend system
- [ ] Workout sharing
- [ ] Comments and likes
- [ ] Leaderboards
- [ ] Challenges

## Privacy
- Opt-in only
- Privacy settings
- Block/report functionality
```

### Issue #9: Nutrition Tracking Module
**Title**: Add Nutrition and Meal Tracking
**Labels**: enhancement, low-priority, feature
**Description**:
```
## Description
Implement comprehensive nutrition tracking.

## Tasks
- [ ] Food database integration
- [ ] Meal logging
- [ ] Calorie counting
- [ ] Macro tracking
- [ ] Nutrition goals

## Integration
- Use existing nutrition API
- Barcode scanning
- Recipe builder
```

### Issue #10: Admin Dashboard
**Title**: Create Admin Panel and Monitoring
**Labels**: enhancement, low-priority, admin
**Description**:
```
## Description
Build admin tools for bot management.

## Tasks
- [ ] User statistics dashboard
- [ ] System health monitoring
- [ ] Broadcast messages
- [ ] User management
- [ ] Analytics and reports

## Security
- Admin authentication
- Audit logging
- Rate limiting
```

## Bug Fixes

### Issue #11: Fix AsyncIO Warnings
**Title**: Resolve AsyncIO Runtime Warnings
**Labels**: bug, low-priority
**Description**:
```
## Description
Fix occasional asyncio warnings in logs.

## Tasks
- [ ] Review async/await usage
- [ ] Fix session management
- [ ] Update deprecated methods
```

### Issue #12: Improve Error Messages
**Title**: Enhance User-Facing Error Messages
**Labels**: bug, ux, medium-priority
**Description**:
```
## Description
Make error messages more helpful and user-friendly.

## Tasks
- [ ] Catalog all error scenarios
- [ ] Write friendly error messages
- [ ] Add recovery suggestions
- [ ] Translate error messages
```

---

## How to Create These Issues

1. Go to: https://github.com/veacheslavv/telegram-gym-bot/issues
2. Click "New Issue"
3. Copy the title and description from above
4. Add the suggested labels
5. Submit the issue

Or use GitHub CLI:
```bash
gh auth login
gh issue create --title "TITLE" --body "DESCRIPTION" --label "LABELS"
```