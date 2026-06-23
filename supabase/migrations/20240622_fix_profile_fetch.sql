-- Create a PostgreSQL function to fetch profiles via RPC
-- This bypasses the 406 error by using RPC instead of REST API

CREATE OR REPLACE FUNCTION get_profile(user_id UUID)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  RETURN (
    SELECT row_to_json(profiles)
    FROM profiles
    WHERE id = user_id
  );
END;
$$;

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION get_profile(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION get_profile(UUID) TO anon;
