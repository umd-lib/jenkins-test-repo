package edu.umd.lib.staffdir;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertTrue;

import java.util.HashMap;
import java.util.Map;

import org.junit.Test;

public class PersonTest {

  @Test(expected = IllegalArgumentException.class)
  public void constructorRequiresNonNullArguments_bothArgumentsNull() {
    Person p = new Person(null, null);
  }

  @Test(expected = IllegalArgumentException.class)
  public void constructorRequiresNonNullArguments_uidArgumentNull() {
    Person p = new Person(null, new HashMap<String, Map<String, String>>());
  }

  @Test(expected = IllegalArgumentException.class)
  public void constructorRequiresNonNullArguments_sourceArgumentNull() {
    Person p = new Person("Test Person", null);
  }

  @Test
  public void testGet_emptySourcesReturnsEmptyString() {
    String uid = "Test Person";
    Map<String, Map<String, String>> sources = new HashMap<>();
    Person p = new Person(uid, sources);

    String value = p.get("NON-EXISTENT SOURCE", "NON-EXISTENT FIELD");
    assertEquals("", value);
  }

  @Test
  public void testGet_existingSourceFieldNotFoundReturnsEmptyString() {
    String uid = "Test Person";
    Map<String, Map<String, String>> sources = new HashMap<>();
    Map<String, String> srcMap = new HashMap<>();
    srcMap.put("EXISTING FIELD", "exists");
    sources.put("EXISTING SOURCE", srcMap);

    Person p = new Person(uid, sources);

    String value = p.get("EXISTING SOURCE", "NON-EXISTENT FIELD");
    assertEquals("", value);
  }

  @Test
  public void testGet_existingSourceNullFieldReturnsEmptyString() {
    String uid = "Test Person";
    Map<String, Map<String, String>> sources = new HashMap<>();
    Map<String, String> srcMap = new HashMap<>();
    srcMap.put("EXISTING FIELD", null);
    sources.put("EXISTING SOURCE", srcMap);

    Person p = new Person(uid, sources);

    String value = p.get("EXISTING SOURCE", "EXISTING FIELD");
    assertEquals("", value);
  }

  @Test
  public void testGet_existingSourceNonNullFieldReturnsValue() {
    String uid = "Test Person";
    Map<String, Map<String, String>> sources = new HashMap<>();
    Map<String, String> srcMap = new HashMap<>();
    srcMap.put("EXISTING FIELD", "exists");
    sources.put("EXISTING SOURCE", srcMap);

    Person p = new Person(uid, sources);

    String value = p.get("EXISTING SOURCE", "EXISTING FIELD");
    assertEquals("exists", value);
  }

  @Test
  public void testGetAllowNull_emptySourcesReturnsNull() {
    String uid = "Test Person";
    Map<String, Map<String, String>> sources = new HashMap<>();
    Person p = new Person(uid, sources);

    String value = p.getAllowNull("NON-EXISTENT SOURCE", "NON-EXISTENT FIELD");
    assertNull(value);
  }

  @Test
  public void testGetAllowNull_existingSourceFieldNotFoundReturnsNull() {
    String uid = "Test Person";
    Map<String, Map<String, String>> sources = new HashMap<>();
    Map<String, String> srcMap = new HashMap<>();
    srcMap.put("EXISTING FIELD", "exists");
    sources.put("EXISTING SOURCE", srcMap);

    Person p = new Person(uid, sources);

    String value = p.getAllowNull("EXISTING SOURCE", "NON-EXISTENT FIELD");
    assertNull(value);
  }

  @Test
  public void testGetAllowNull_existingSourceNullFieldReturnsEmptyString() {
    String uid = "Test Person";
    Map<String, Map<String, String>> sources = new HashMap<>();
    Map<String, String> srcMap = new HashMap<>();
    srcMap.put("EXISTING FIELD", null);
    sources.put("EXISTING SOURCE", srcMap);

    Person p = new Person(uid, sources);

    String value = p.getAllowNull("EXISTING SOURCE", "EXISTING FIELD");
    assertNull(value);
  }

  @Test
  public void testGetAllowNull_existingSourceNonNullFieldReturnsValue() {
    String uid = "Test Person";
    Map<String, Map<String, String>> sources = new HashMap<>();
    Map<String, String> srcMap = new HashMap<>();
    srcMap.put("EXISTING FIELD", "exists");
    sources.put("EXISTING SOURCE", srcMap);

    Person p = new Person(uid, sources);

    String value = p.getAllowNull("EXISTING SOURCE", "EXISTING FIELD");
    assertEquals("exists", value);
  }

  @Test
  public void testToString() {
    Person p = new Person("Test Person", new HashMap<String, Map<String, String>>());
    String str = p.toString();
    assertTrue(str.startsWith("Person@"));
  }
}
