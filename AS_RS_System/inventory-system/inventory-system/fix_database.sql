-- Fix corrupt database statuses
-- All compartments with status 'Free' and item_id=NULL should be 'Empty'
UPDATE SubCompartments 
SET status = 'Empty' 
WHERE status = 'Free' AND item_id IS NULL;

-- Verify the fix
SELECT status, COUNT(*) as count 
FROM SubCompartments 
GROUP BY status;

-- Show current inventory counts after fix
SELECT 
    i.item_id,
    i.name,
    COUNT(sc.subcom_place) as available_count
FROM Items i
LEFT JOIN SubCompartments sc ON i.item_id = sc.item_id AND sc.status = 'Occupied'
GROUP BY i.item_id, i.name
ORDER BY i.item_id;
